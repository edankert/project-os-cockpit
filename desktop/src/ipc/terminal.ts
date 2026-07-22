// Native terminal pane backend (TASK-0063 + TASK-0104).
//
// One node-pty per workspace, keyed by workspaceId. PTYs persist
// across workspace switches in the renderer — switching tabs does NOT
// kill the shell — so the user keeps long-running REPLs / dev servers
// alive while flipping between projects.
//
// Each PTY records its output into a small ring-buffered backlog
// (~256 KB), so when the renderer reattaches (`terminal:attach`) it
// can rewrite the xterm with the last backlog and resume in-place.
//
// PTYs are owned by main; the renderer is a view.
//
// Survivability (ISS-0008 / TASK-0144): when tmux ≥ 3.2 is available,
// the PTY is a tmux *client* attached to a named session on a
// dedicated socket (`-L cockpit`) — the tmux server owns the shell.
// App death (crash, kill, quit) only detaches the client; the next
// launch runs `new-session -A` and lands back in the still-running
// session, so an in-flight claude/codex keeps working across app
// restarts. Explicit dispose kills the session too; app shutdown
// deliberately does NOT — that asymmetry is the feature. Without
// tmux we fall back to the previous direct spawn (PTY dies with the
// app) and print a resume hint when the last session died unclean
// (TASK-0145). COCKPIT_NO_TMUX=1 forces the fallback.

import { BrowserWindow, app, ipcMain } from 'electron';
import { execFile, execFileSync } from 'node:child_process';
import * as fs from 'node:fs';
import * as os from 'node:os';
import * as path from 'node:path';
import * as pty from 'node-pty';

import { ensureInstrumentation } from './agent-instrument';

const BACKLOG_MAX_BYTES = 256 * 1024;  // 256 KB scrollback per workspace

interface PtyRecord {
  workspaceId: string;
  windowId: number;     // window that owns the renderer the data is fanned to
  pty: pty.IPty;
  /** Chunks since spawn, capped at BACKLOG_MAX_BYTES total. */
  backlog: string[];
  backlogBytes: number;
  /** True when this PTY is a tmux client (session survives us). */
  viaTmux: boolean;
}

const ptys = new Map<string, PtyRecord>();

// ---- tmux backing (ISS-0008 / TASK-0144) ----

const TMUX_SOCKET = 'cockpit';
let tmuxResolved: string | null | undefined; // undefined = not yet probed

/** Locate a tmux ≥ 3.2 binary (3.2 introduced `new-session -e`, which
 * we need for per-session instrumentation env). GUI apps don't get the
 * user's shell PATH, so probe the common install locations too. */
function tmuxBinary(): string | null {
  if (process.env.COCKPIT_NO_TMUX) return null;
  if (tmuxResolved !== undefined) return tmuxResolved;
  const candidates = [
    '/opt/homebrew/bin/tmux',
    '/usr/local/bin/tmux',
    '/usr/bin/tmux',
    ...(process.env.PATH || '').split(':').filter(Boolean).map((d) => path.join(d, 'tmux')),
  ];
  tmuxResolved = null;
  for (const cand of candidates) {
    try {
      if (!fs.existsSync(cand)) continue;
      const out = execFileSync(cand, ['-V'], { encoding: 'utf-8', timeout: 3000 }).trim();
      const m = /tmux\s+(\d+)\.(\d+)/.exec(out);
      if (!m) continue;
      const major = Number(m[1]);
      const minor = Number(m[2]);
      if (major > 3 || (major === 3 && minor >= 2)) {
        tmuxResolved = cand;
        break;
      }
    } catch { /* unusable candidate — try the next */ }
  }
  return tmuxResolved;
}

function tmuxSessionName(workspaceId: string): string {
  return `cockpit-${workspaceId.replace(/[^A-Za-z0-9_-]/g, '-')}`.slice(0, 48);
}

/** Minimal generated config on our dedicated socket so the user's own
 * ~/.tmux.conf, status bar, and sessions are never touched. */
function ensureTmuxConf(): string {
  const dir = path.join(app.getPath('userData'), 'instrument');
  fs.mkdirSync(dir, { recursive: true });
  const conf = path.join(dir, 'cockpit.tmux.conf');
  fs.writeFileSync(conf, [
    'set -g status off',
    'set -g history-limit 100000',
    'set -sg escape-time 10',
    'set -g default-terminal "screen-256color"',
    'setw -g aggressive-resize on',
    '',
  ].join('\n'), 'utf-8');
  return conf;
}

/** Resume hint (TASK-0145): fallback spawns only — if the workspace's
 * session index shows a recent session with no SessionEnd, the shell
 * it ran in died with us. Fan a display-only line to the renderer;
 * nothing is typed into the shell. */
function deathHint(root: string): string | null {
  try {
    const raw = fs.readFileSync(path.join(root, '.cockpit', 'sessions.json'), 'utf-8');
    const data = JSON.parse(raw);
    const sessions = Array.isArray(data) ? data : data?.sessions;
    if (!Array.isArray(sessions)) return null;
    for (const s of sessions) {
      if (!s || typeof s !== 'object' || s.ended) continue;
      const last = Date.parse(s.last_event ?? s.started ?? '');
      if (!Number.isFinite(last) || Date.now() - last > 24 * 3600_000) continue;
      const agent = typeof s.agent === 'string' ? s.agent : 'agent';
      if (agent !== 'claude' || typeof s.session_id !== 'string') continue;
      return `\r\n\x1b[33m⚡ cockpit: a previous claude session died with the app — resume: claude --resume ${s.session_id}\x1b[0m\r\n`;
    }
  } catch { /* no index / unreadable — no hint */ }
  return null;
}

function defaultShell(): string {
  return process.env.SHELL || (process.platform === 'win32' ? 'powershell.exe' : '/bin/zsh');
}

function send(window: BrowserWindow, channel: string, payload: unknown): void {
  if (!window || window.isDestroyed()) return;
  window.webContents.send(channel, payload);
}

function appendBacklog(record: PtyRecord, chunk: string): void {
  record.backlog.push(chunk);
  record.backlogBytes += chunk.length;
  // Drop oldest chunks until we're back under the cap.
  while (record.backlogBytes > BACKLOG_MAX_BYTES && record.backlog.length > 1) {
    const dropped = record.backlog.shift();
    if (dropped) record.backlogBytes -= dropped.length;
  }
}

interface SpawnOpts {
  workspaceId: string;
  cwd?: string;
  cols?: number;
  rows?: number;
}

function spawnPty(window: BrowserWindow, opts: SpawnOpts): PtyRecord {
  // If a PTY already exists for this workspace, hand it back rather
  // than re-spawning. Spawn is idempotent from the renderer's POV.
  const existing = ptys.get(opts.workspaceId);
  if (existing) {
    existing.windowId = window.id;
    return existing;
  }
  const shell = defaultShell();
  const cwd = opts.cwd && opts.cwd.length > 0 ? opts.cwd : os.homedir();
  // Agent instrumentation (FEAT-0019): generated ZDOTDIR wraps
  // claude/codex so sessions started in this PTY feed the sidecar's
  // /api/agent-hook. zsh-only injection — other shells still work,
  // just uninstrumented. COCKPIT_NO_INSTRUMENT=1 disables.
  const instrument = shell.endsWith('zsh')
    ? ensureInstrumentation(opts.workspaceId)
    : null;
  const env = {
    ...process.env,
    TERM: 'xterm-256color',
    ...(instrument ? instrument.env : {}),
  };
  const tmux = tmuxBinary();
  let proc: pty.IPty;
  if (tmux) {
    // tmux client attach-or-create. Session env (-e) only applies at
    // creation; on reattach the original instrumentation env persists,
    // and COCKPIT_HOOK_URL flows through the hook-env file re-sourced
    // per event, so surviving sessions re-target the new sidecar port
    // after an app restart on their own.
    const args = [
      '-L', TMUX_SOCKET, '-f', ensureTmuxConf(),
      'new-session', '-A',
      '-s', tmuxSessionName(opts.workspaceId),
      '-c', cwd,
    ];
    for (const [key, value] of Object.entries(instrument?.env ?? {})) {
      args.push('-e', `${key}=${value}`);
    }
    proc = pty.spawn(tmux, args, {
      name: 'xterm-256color',
      cols: opts.cols ?? 80,
      rows: opts.rows ?? 24,
      cwd,
      env,
    });
  } else {
    proc = pty.spawn(shell, [], {
      name: 'xterm-256color',
      cols: opts.cols ?? 80,
      rows: opts.rows ?? 24,
      cwd,
      env,
    });
  }
  const record: PtyRecord = {
    workspaceId: opts.workspaceId,
    windowId: window.id,
    pty: proc,
    backlog: [],
    backlogBytes: 0,
    viaTmux: Boolean(tmux),
  };
  ptys.set(opts.workspaceId, record);
  if (!tmux) {
    // Fallback shells die with us — surface how to pick the pieces up.
    const hint = deathHint(cwd);
    if (hint) {
      setTimeout(() => {
        if (ptys.get(record.workspaceId) !== record) return;
        appendBacklog(record, hint);
        const target = BrowserWindow.fromId(record.windowId);
        if (target) send(target, 'terminal:data', { workspaceId: record.workspaceId, data: hint });
      }, 700);
    }
  }

  proc.onData((data: string) => {
    appendBacklog(record, data);
    // Always fan to the window that most recently attached, not the
    // window the PTY was originally spawned in — so when the user
    // opens a workspace in a second window, the data lands there.
    const target = BrowserWindow.fromId(record.windowId);
    if (target) send(target, 'terminal:data', { workspaceId: record.workspaceId, data });
  });
  proc.onExit(({ exitCode, signal }) => {
    // Identity guard (same pattern as the deathHint above): a restart
    // disposes then immediately respawns the same workspace, and node-pty's
    // onExit is async — it can fire AFTER the fresh record is installed. If
    // we deleted by key unconditionally we'd remove the new PTY and emit a
    // spurious exit into the fresh console. Only act if this is still the
    // current record (TASK-0187).
    if (ptys.get(record.workspaceId) !== record) return;
    ptys.delete(record.workspaceId);
    const target = BrowserWindow.fromId(record.windowId);
    if (target) send(target, 'terminal:exit', { workspaceId: record.workspaceId, exitCode, signal });
  });
  return record;
}

async function killPty(workspaceId: string): Promise<void> {
  const record = ptys.get(workspaceId);
  if (!record) return;
  ptys.delete(workspaceId);
  try { record.pty.kill(); } catch { /* already gone */ }
  // Explicit dispose means "close this terminal", so the backing tmux
  // session goes too — otherwise it would linger invisibly forever. AWAIT
  // the kill so the wedged session is provably gone before any respawn: a
  // restart's `tmux new-session -A` (attach-if-exists) would otherwise race
  // the async kill and reattach the very session we're trying to destroy
  // (TASK-0187).
  if (record.viaTmux) {
    const tmux = tmuxBinary();
    if (tmux) {
      await new Promise<void>((resolve) => {
        execFile(tmux, ['-L', TMUX_SOCKET, 'kill-session', '-t', tmuxSessionName(workspaceId)],
          { timeout: 3000 },
          () => resolve() /* best-effort — session may already be gone / hung */);
      });
    }
  }
}

/** Type into a workspace's PTY regardless of which window shows it
 * (FEAT-0025 dispatch delivery). Returns false when no PTY exists. */
export function writeToPty(workspaceId: string, data: string): boolean {
  const record = ptys.get(workspaceId);
  if (!record) return false;
  record.pty.write(data);
  return true;
}

export function hasPty(workspaceId: string): boolean {
  return ptys.has(workspaceId);
}

/** True when the workspace terminal survives app death (quit-guard
 * input, TASK-0145). */
export function isTmuxBacked(workspaceId: string): boolean {
  return ptys.get(workspaceId)?.viaTmux ?? false;
}

export function shutdownAllTerminals(): void {
  // Kills only our PTYs. For tmux-backed terminals that's just the
  // client — the session (and any agent inside it) keeps running and
  // the next launch reattaches (ISS-0008).
  for (const record of ptys.values()) {
    try { record.pty.kill(); } catch { /* already gone */ }
  }
  ptys.clear();
}

interface TerminalIpcDeps {
  getActiveWindow: () => BrowserWindow | null;
}

export function registerTerminalIpc(_deps: TerminalIpcDeps): void {
  ipcMain.handle('terminal:spawn', (evt, opts: SpawnOpts) => {
    const window = BrowserWindow.fromWebContents(evt.sender);
    if (!window) return { ok: false, error: 'no window' };
    if (!opts?.workspaceId) return { ok: false, error: 'workspaceId required' };
    spawnPty(window, opts);
    return { ok: true };
  });

  // Attach: re-bind the named PTY to this window and return the
  // backlog so the renderer can rewrite the xterm in-place.
  ipcMain.handle('terminal:attach', (evt, payload: { workspaceId: string }) => {
    const window = BrowserWindow.fromWebContents(evt.sender);
    if (!window) return { ok: false, error: 'no window', backlog: '' };
    const record = ptys.get(payload.workspaceId);
    if (!record) return { ok: false, error: 'no pty', backlog: '' };
    record.windowId = window.id;
    return { ok: true, backlog: record.backlog.join('') };
  });

  ipcMain.on('terminal:input', (_evt, payload: { workspaceId: string; data: string }) => {
    const record = ptys.get(payload?.workspaceId);
    if (!record) return;
    record.pty.write(payload.data);
  });

  ipcMain.on('terminal:resize', (_evt, payload: { workspaceId: string; cols: number; rows: number }) => {
    const record = ptys.get(payload?.workspaceId);
    if (!record) return;
    try { record.pty.resize(payload.cols, payload.rows); }
    catch { /* PTY may have already died; ignore */ }
  });

  ipcMain.handle('terminal:dispose', async (_evt, payload: { workspaceId: string }) => {
    if (!payload?.workspaceId) return { ok: false };
    await killPty(payload.workspaceId);
    return { ok: true };
  });
}
