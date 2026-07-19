// Main-process dispatch runtime (FEAT-0025 / TASK-0134).
//
// The FEAT-0024 first cut kept the dispatch queue in the renderer,
// pinned to the active workspace — queued work for a background
// workspace never delivered and an app restart lost the queue. PTYs
// and the cross-workspace agent-state poller live HERE, so the queue
// and its delivery state machine do too; renderers are views.
//
// Flow:
//   renderer → dispatch:execute {workspaceId, item}
//     busy/needs-input      → enqueue (persisted) + broadcast
//     waiting + live session → type raw prompt into the REPL
//     otherwise             → run `<agent> '<prompt>'` in the shell
//   poller/SSE-poke state transition (waiting|idle) → deliver next.
//
// Prompts are single-quote shell-escaped ('\'' splice) so `$(…)`,
// backticks, and history `!` in note-derived text stay inert.

import { BrowserWindow, app, ipcMain } from 'electron';
import * as fs from 'node:fs';
import * as http from 'node:http';
import * as path from 'node:path';

import { hasPty, writeToPty } from './terminal';
import { sidecarUrlFor } from './sidecar';

export interface DispatchItem {
  id: string;
  rel: string;
  verb?: string;
  agent: 'claude' | 'codex';
  prompt: string;
  ts: string;
}

interface ExecuteResult {
  queued: boolean;
  delivered?: 'shell' | 'repl';
  warning?: string;
}

const QUEUE_MAX = 20;

const queues = new Map<string, DispatchItem[]>();
const lastKnownState = new Map<string, string>();
let persistTimer: NodeJS.Timeout | null = null;

function queuePath(): string {
  return path.join(app.getPath('userData'), 'dispatch-queues.json');
}

function loadQueues(): void {
  try {
    const raw = JSON.parse(fs.readFileSync(queuePath(), 'utf-8')) as unknown;
    if (raw && typeof raw === 'object') {
      for (const [wsId, items] of Object.entries(raw as Record<string, unknown>)) {
        if (Array.isArray(items)) {
          queues.set(wsId, items.filter(isValidItem).slice(0, QUEUE_MAX));
        }
      }
    }
  } catch { /* first run / unreadable — start empty */ }
}

function isValidItem(raw: unknown): raw is DispatchItem {
  if (!raw || typeof raw !== 'object') return false;
  const it = raw as Record<string, unknown>;
  return typeof it.id === 'string' && typeof it.rel === 'string'
    && typeof it.prompt === 'string' && it.prompt.length > 0
    && (it.agent === 'claude' || it.agent === 'codex');
}

function persistSoon(): void {
  if (persistTimer) clearTimeout(persistTimer);
  persistTimer = setTimeout(() => {
    persistTimer = null;
    try {
      const out: Record<string, DispatchItem[]> = {};
      for (const [wsId, items] of queues) {
        if (items.length > 0) out[wsId] = items;
      }
      fs.writeFileSync(queuePath(), JSON.stringify(out), 'utf-8');
    } catch (err) {
      console.error('[dispatch-queue] persist failed:', err);
    }
  }, 250);
}

function queueOf(workspaceId: string): DispatchItem[] {
  let q = queues.get(workspaceId);
  if (!q) { q = []; queues.set(workspaceId, q); }
  return q;
}

/** Pending dispatch count for a workspace (fleet view, TASK-0150). */
export function queueDepthFor(workspaceId: string): number {
  return queues.get(workspaceId)?.length ?? 0;
}

function broadcast(channel: string, payload: unknown): void {
  for (const win of BrowserWindow.getAllWindows()) {
    if (!win.isDestroyed()) win.webContents.send(channel, payload);
  }
}

function broadcastQueue(workspaceId: string): void {
  broadcast('dispatch:queue-changed', {
    workspaceId, items: queueOf(workspaceId).slice(),
  });
}

function shellEscapeSingle(text: string): string {
  return `'${text.replace(/'/g, `'\\''`)}'`;
}

// ---- sidecar helpers ----

function fetchJson(url: string, timeoutMs = 2000): Promise<unknown | null> {
  return new Promise((resolve) => {
    const req = http.get(url, { timeout: timeoutMs }, (res) => {
      let body = '';
      res.on('data', (chunk: Buffer) => { body += chunk.toString('utf-8'); });
      res.on('end', () => {
        try { resolve(JSON.parse(body)); } catch { resolve(null); }
      });
    });
    req.on('error', () => resolve(null));
    req.on('timeout', () => { req.destroy(); resolve(null); });
  });
}

function postJson(url: string, body: unknown): void {
  const data = Buffer.from(JSON.stringify(body), 'utf-8');
  const u = new URL(url);
  const req = http.request({
    hostname: u.hostname, port: u.port, path: u.pathname, method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Content-Length': data.length },
    timeout: 2000,
  });
  req.on('error', () => { /* ledger is best-effort */ });
  req.end(data);
}

async function liveSessionInfo(
  workspaceId: string,
): Promise<{ live: boolean; agent: string | null }> {
  const base = sidecarUrlFor(workspaceId);
  if (!base) return { live: false, agent: null };
  const snap = await fetchJson(`${base}/api/cockpit/state`) as
    { session?: { live?: boolean; agent?: string | null } | null } | null;
  const session = snap?.session;
  return {
    live: session?.live === true,
    agent: (session?.agent as string | undefined) ?? null,
  };
}

function recordLedger(workspaceId: string, item: DispatchItem): void {
  const base = sidecarUrlFor(workspaceId);
  if (!base) return;
  postJson(`${base}/api/cockpit/dispatch`, {
    id: item.id, verb: item.verb, agent: item.agent,
  });
}

// ---- delivery state machine ----

async function deliver(
  workspaceId: string, item: DispatchItem, state: string,
): Promise<ExecuteResult> {
  const session = await liveSessionInfo(workspaceId);
  const mode: 'shell' | 'repl' =
    state === 'waiting' && session.live ? 'repl' : 'shell';
  let warning: string | undefined;
  if (mode === 'repl' && session.agent && session.agent !== item.agent) {
    warning = `live session is ${session.agent} — delivered there instead of ${item.agent}`;
  }
  const data = mode === 'repl'
    ? item.prompt + '\r'
    : `${item.agent} ${shellEscapeSingle(item.prompt)}\r`;
  if (!writeToPty(workspaceId, data)) {
    // No terminal for this workspace yet — hold in the queue; the next
    // state transition (or terminal open + transition) retries.
    const q = queueOf(workspaceId);
    q.unshift(item);
    q.splice(QUEUE_MAX);
    persistSoon();
    broadcastQueue(workspaceId);
    return { queued: true, warning: 'no terminal open — queued' };
  }
  recordLedger(workspaceId, item);
  broadcast('dispatch:delivered', { workspaceId, item, mode, warning });
  return { queued: false, delivered: mode, warning };
}

export async function executeDispatch(
  workspaceId: string, item: DispatchItem,
): Promise<ExecuteResult> {
  const state = lastKnownState.get(workspaceId) ?? 'idle';
  if (state === 'busy' || state === 'needs-input') {
    const q = queueOf(workspaceId);
    q.push(item);
    q.splice(QUEUE_MAX);
    persistSoon();
    broadcastQueue(workspaceId);
    return { queued: true };
  }
  return deliver(workspaceId, item, state);
}

let delivering = false;

/**
 * Feed a workspace's agent-state transition into the queue runtime.
 * Called by the cross-workspace poller (all workspaces, ~5s cadence)
 * and by the renderer's SSE poke (active workspace, instant).
 */
export function onAgentStateChanged(
  workspaceId: string, newState: string | undefined, opts: { deliver?: boolean } = {},
): void {
  if (!newState) return;
  lastKnownState.set(workspaceId, newState);
  if (opts.deliver === false) return;
  if (newState !== 'waiting' && newState !== 'idle') return;
  const q = queues.get(workspaceId);
  if (!q || q.length === 0 || delivering) return;
  const item = q.shift()!;
  persistSoon();
  broadcastQueue(workspaceId);
  delivering = true;
  void deliver(workspaceId, item, newState).finally(() => {
    delivering = false;
  });
}

export function registerDispatchIpc(): void {
  loadQueues();

  ipcMain.handle(
    'dispatch:execute',
    async (_evt, workspaceId: string, item: unknown): Promise<ExecuteResult | { error: string }> => {
      if (typeof workspaceId !== 'string' || !workspaceId) {
        return { error: 'workspaceId required' };
      }
      if (!isValidItem(item)) return { error: 'invalid dispatch item' };
      return executeDispatch(workspaceId, item);
    },
  );

  ipcMain.handle('dispatch:list', (_evt, workspaceId: string) =>
    queueOf(String(workspaceId)).slice());

  ipcMain.handle('dispatch:remove', (_evt, workspaceId: string, index: number) => {
    const q = queueOf(String(workspaceId));
    if (Number.isInteger(index) && index >= 0 && index < q.length) {
      q.splice(index, 1);
      persistSoon();
      broadcastQueue(String(workspaceId));
    }
    return q.slice();
  });

  ipcMain.handle('dispatch:clear', (_evt, workspaceId: string) => {
    queues.set(String(workspaceId), []);
    persistSoon();
    broadcastQueue(String(workspaceId));
    return [];
  });

  ipcMain.on('dispatch:poke', (_evt, payload: { workspaceId?: string; state?: string }) => {
    if (payload?.workspaceId) {
      onAgentStateChanged(payload.workspaceId, payload.state);
    }
  });
}

export function hasTerminal(workspaceId: string): boolean {
  return hasPty(workspaceId);
}
