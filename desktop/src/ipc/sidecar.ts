// Python sidecar lifecycle (TASK-0061).
//
// One project_os_cockpit child process per workspace window:
//
//   1. Pick a free port in 8765–8865 via portfinder.
//   2. spawn(python, ['-m', 'project_os_cockpit', '<docs>', '--port', ...,
//                     '--bind', '127.0.0.1', '--no-open'],
//          env={ COCKPIT_DESKTOP: '1', PYTHONUNBUFFERED: '1' }).
//   3. Poll GET /healthz until 200 (or 10s timeout).
//   4. Tell the renderer the URL is ready; the renderer mounts it in
//      the iframe.
//   5. On window close or workspace switch: SIGTERM, wait 3s, SIGKILL.
//
// The Python interpreter is resolved via:
//   COCKPIT_DESKTOP_PYTHON env var — explicit override, used during
//                                    development (e.g. `.venv/bin/python`)
//   'python3' on PATH             — fallback
// TASK-0062 replaces this with a bundled python-build-standalone runtime
// shipped inside the .app, so the user never needs a system Python.

import { BrowserWindow, app, ipcMain } from 'electron';
import { ChildProcess, spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import * as http from 'node:http';
import * as path from 'node:path';

import { getPortPromise } from 'portfinder';

import { getWorkspace, markOpened } from './workspaces';
import { subscribeAgentFocus, unsubscribeAgentFocus } from './agent-focus';
import { setSidecarUrl } from './agent-instrument';
import type {
  SidecarExitedPayload,
  SidecarFailedPayload,
  SidecarReadyPayload,
  Workspace,
} from '../types';

interface SidecarRecord {
  workspaceId: string;
  windowId: number;     // window currently bound to receive this sidecar's events
  process: ChildProcess;
  port: number;
  url: string;
  stderrTail: string[];
}

// workspaceId → record. Sidecars are per-workspace, not per-window:
// switching workspace inside the same window REUSES the running sidecar
// rather than killing + respawning. This avoids burning through the
// 100-port range (8765–8865) — each switch used to leak a port into
// TIME_WAIT for ~30–120 s on macOS, exhausting the range fast.
// Sidecars only die on explicit dispose, natural crash, or app exit.
const sidecars = new Map<string, SidecarRecord>();

function pythonExecutable(): string {
  // 1. Explicit override (development — e.g. point at `.venv/bin/python`).
  if (process.env.COCKPIT_DESKTOP_PYTHON) {
    return process.env.COCKPIT_DESKTOP_PYTHON;
  }
  // 2. Bundled python-build-standalone runtime (TASK-0062).
  const bundled = bundledPythonPath();
  if (bundled) return bundled;
  // 3. System python3 as last resort. After TASK-0065 packages the .app
  // with a bundled runtime, this branch should not fire in production.
  return 'python3';
}

function bundledPythonPath(): string | null {
  const archKey = `${process.platform}-${process.arch}`;
  const relSuffix = process.platform === 'win32'
    ? path.join('python-runtime', archKey, 'python', 'python.exe')
    : path.join('python-runtime', archKey, 'python', 'bin', 'python3');
  // In dev: `<desktop-package>/python-runtime/<arch>/python/…`.
  // In packaged app: same layout under `<resourcesPath>`.
  const candidates = [
    path.join(app.getAppPath(), relSuffix),
    process.resourcesPath
      ? path.join(process.resourcesPath, relSuffix)
      : null,
  ].filter((p): p is string => Boolean(p));
  for (const candidate of candidates) {
    if (existsSync(candidate)) return candidate;
  }
  return null;
}

function send(
  window: BrowserWindow | null,
  ev: { kind: string; payload?: unknown },
): void {
  if (!window || window.isDestroyed()) return;
  window.webContents.send('sidecar:event', ev);
}

async function pollHealthz(port: number, timeoutMs = 10_000): Promise<boolean> {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const ready = await new Promise<boolean>((resolve) => {
      const req = http.get(
        { host: '127.0.0.1', port, path: '/healthz', timeout: 1000 },
        (res) => {
          const ok = res.statusCode === 200;
          // Drain the body so the socket can close cleanly.
          res.resume();
          resolve(ok);
        },
      );
      req.on('error', () => resolve(false));
      req.on('timeout', () => {
        req.destroy();
        resolve(false);
      });
    });
    if (ready) return true;
    await new Promise((r) => setTimeout(r, 200));
  }
  return false;
}

function killProcess(proc: ChildProcess): void {
  if (proc.exitCode != null || proc.signalCode != null) return;
  try {
    proc.kill('SIGTERM');
  } catch {
    /* already gone */
  }
  const timer = setTimeout(() => {
    if (proc.exitCode == null && proc.signalCode == null) {
      try {
        proc.kill('SIGKILL');
      } catch {
        /* already gone */
      }
    }
  }, 3000);
  proc.once('exit', () => clearTimeout(timer));
}

function killSidecarFor(workspaceId: string): void {
  const record = sidecars.get(workspaceId);
  if (!record) return;
  sidecars.delete(workspaceId);
  const window = BrowserWindow.fromId(record.windowId);
  if (window) unsubscribeAgentFocus(window);
  killProcess(record.process);
}

async function spawnSidecar(
  workspace: Workspace,
  window: BrowserWindow,
): Promise<void> {
  // If a sidecar already exists for this workspace AND its process is
  // still alive, re-bind the window and re-emit `ready` so the renderer
  // picks up where it left off. No new spawn → no new port consumed.
  const existing = sidecars.get(workspace.id);
  if (existing && existing.process.exitCode == null && existing.process.signalCode == null) {
    existing.windowId = window.id;
    subscribeAgentFocus(window, existing.url);
    setSidecarUrl(workspace.id, existing.url);
    void markOpened(workspace.id);
    send(window, {
      kind: 'ready',
      payload: {
        workspaceId: workspace.id,
        port: existing.port,
        url: existing.url,
      } satisfies SidecarReadyPayload,
    });
    return;
  }
  // Drop any dead-but-still-tracked record so we re-spawn cleanly.
  if (existing) sidecars.delete(workspace.id);

  const port = await getPortPromise({ port: 8765, stopPort: 8865 });
  const py = pythonExecutable();
  const docsDir = path.join(workspace.root, 'docs');

  const child = spawn(
    py,
    [
      '-m', 'project_os_cockpit',
      docsDir,
      '--port', String(port),
      '--bind', '127.0.0.1',
      '--no-open',
    ],
    {
      cwd: workspace.root,
      env: {
        ...process.env,
        COCKPIT_DESKTOP: '1',
        PYTHONUNBUFFERED: '1',
      },
      stdio: ['ignore', 'pipe', 'pipe'],
    },
  );

  const stderrTail: string[] = [];
  child.stderr?.on('data', (data: Buffer) => {
    for (const line of data.toString('utf-8').split('\n')) {
      if (!line.trim()) continue;
      stderrTail.push(line);
      if (stderrTail.length > 50) stderrTail.shift();
    }
  });

  const url = `http://127.0.0.1:${port}`;
  const record: SidecarRecord = {
    workspaceId: workspace.id,
    windowId: window.id,
    process: child,
    port,
    url,
    stderrTail,
  };

  // Register before health check so a window-close during the poll
  // still tears down the child via shutdownAllSidecars().
  sidecars.set(workspace.id, record);

  child.on('exit', (code, signal) => {
    sidecars.delete(workspace.id);
    const target = BrowserWindow.fromId(record.windowId);
    const payload: SidecarExitedPayload = {
      workspaceId: workspace.id,
      code,
      signal,
    };
    send(target, { kind: 'exited', payload });
  });

  // If the process dies before becoming healthy, surface that as a
  // 'failed' rather than a misleading 'exited'.
  let exitedBeforeReady = false;
  child.once('exit', () => {
    exitedBeforeReady = true;
  });

  const ready = await pollHealthz(port);
  if (!ready || exitedBeforeReady) {
    const payload: SidecarFailedPayload = {
      workspaceId: workspace.id,
      reason: exitedBeforeReady
        ? 'sidecar exited before becoming healthy'
        : 'sidecar did not respond to /healthz within 10s',
      stderrTail: stderrTail.slice(-10).join('\n') || undefined,
    };
    send(window, { kind: 'failed', payload });
    killProcess(child);
    return;
  }

  await markOpened(workspace.id);
  subscribeAgentFocus(window, url);
  // Point the instrumentation scripts (FEAT-0019) at the live sidecar.
  setSidecarUrl(workspace.id, url);
  const readyPayload: SidecarReadyPayload = {
    workspaceId: workspace.id,
    port,
    url,
  };
  send(window, { kind: 'ready', payload: readyPayload });
}

/** Live sidecar base URL for a workspace, or null (FEAT-0025). */
export function sidecarUrlFor(workspaceId: string): string | null {
  const rec = sidecars.get(workspaceId);
  if (!rec) return null;
  if (rec.process.exitCode != null || rec.process.signalCode != null) return null;
  return rec.url;
}

export function shutdownAllSidecars(): void {
  for (const record of sidecars.values()) {
    killProcess(record.process);
  }
  sidecars.clear();
}

interface SidecarIpcDeps {
  getActiveWindow: () => BrowserWindow | null;
}

export function registerSidecarIpc(deps: SidecarIpcDeps): void {
  ipcMain.handle(
    'workspaces:open',
    async (_evt, id: string): Promise<{ ok: boolean; error?: string }> => {
      const workspace = getWorkspace(id);
      if (!workspace) {
        return { ok: false, error: `unknown workspace: ${id}` };
      }
      const window = deps.getActiveWindow();
      if (!window) {
        return { ok: false, error: 'no active window' };
      }

      // Sidecars persist per-workspace (FEAT-0015 fix): switching back
      // to a previously-opened workspace reuses its running sidecar
      // instead of spawning a fresh process. spawnSidecar() is
      // idempotent — it returns early after re-emitting `ready` when
      // a live record already exists.
      spawnSidecar(workspace, window).catch((err: unknown) => {
        const payload: SidecarFailedPayload = {
          workspaceId: workspace.id,
          reason: String(err),
        };
        send(window, { kind: 'failed', payload });
      });

      return { ok: true };
    },
  );
}
