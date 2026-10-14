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
//     live Claude session    → hand to the sidecar as a delivery; the
//                              cockpit plugin in that session submits it
//                              once the session is idle (FEAT-0158).
//                              Nothing is typed into a Claude terminal.
//     busy/needs-input      → enqueue (persisted) + broadcast
//   otherwise, by what runs in the terminal's foreground (TASK-0660):
//     Codex                 → paste the prompt, then Return
//     a shell               → run `<agent> '<prompt>'`
//     Claude, unreachable   → hold in the queue
//     anything else         → hold in the queue
//   poller/SSE-poke state transition (waiting|idle) → deliver next.
//
// Prompts are single-quote shell-escaped ('\'' splice) so `$(…)`,
// backticks, and history `!` in note-derived text stay inert.

import { BrowserWindow, app, ipcMain } from 'electron';
import * as fs from 'node:fs';
import * as http from 'node:http';
import * as path from 'node:path';

import { foregroundCommand, hasPty, writeToPty } from './terminal';
import { sidecarUrlFor } from './sidecar';

export interface DispatchItem {
  id: string;
  rel: string;
  verb?: string;
  /** Agent id from the served registry (ISS-0032). Open by design:
   *  the queue must not discard work for an agent this build of the
   *  renderer happens not to know about. */
  agent: string;
  prompt: string;
  ts: string;
}

interface ExecuteResult {
  queued: boolean;
  /** `submit`: handed to the sidecar for the cockpit plugin to submit. */
  delivered?: 'shell' | 'repl' | 'submit';
  /** The sidecar's delivery, when `delivered` is `submit`. */
  delivery?: Delivery;
  warning?: string;
}

/** A dispatched prompt the sidecar holds for one Claude session (FEAT-0158). */
export interface Delivery {
  did: string;
  id: string;
  verb?: string;
  prompt: string;
  session_id: string;
  state: string;
  reason?: string;
  /** `you` while the person has stopped the session with Esc (TASK-0659). */
  waiting_for?: string;
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
    // Membership is NOT checked here. It used to be `it.agent === 'claude' ||
    // it.agent === 'codex'`, which meant a queued item for any other agent
    // failed validation and was discarded, silently, on the next restart --
    // the exact opposite of FEAT-0025's promise that the queue survives a
    // restart (ISS-0032). Shape is this function's job; membership belongs to
    // the registry, and an item naming an unknown agent is bad configuration,
    // not corrupt data.
    && typeof it.agent === 'string' && it.agent.length > 0;
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

/** POST JSON and read the answer; null when the sidecar did not answer. */
function postJsonResult(url: string, body: unknown, timeoutMs = 2000): Promise<{ status: number; json: any } | null> {
  return new Promise((resolve) => {
    const data = Buffer.from(JSON.stringify(body), 'utf-8');
    const u = new URL(url);
    const req = http.request({
      hostname: u.hostname, port: u.port, path: u.pathname, method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': data.length },
      timeout: timeoutMs,
    }, (res) => {
      let text = '';
      res.on('data', (chunk: Buffer) => { text += chunk.toString('utf-8'); });
      res.on('end', () => {
        try { resolve({ status: res.statusCode ?? 0, json: JSON.parse(text) }); } catch { resolve(null); }
      });
    });
    req.on('error', () => resolve(null));
    req.on('timeout', () => { req.destroy(); resolve(null); });
    req.end(data);
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

export interface LiveSession {
  live: boolean;
  agent: string | null;
  sessionId: string | null;
}

async function liveSessionInfo(workspaceId: string): Promise<LiveSession> {
  const base = sidecarUrlFor(workspaceId);
  if (!base) return { live: false, agent: null, sessionId: null };
  const snap = await fetchJson(`${base}/api/cockpit/state`) as
    { session?: { live?: boolean; agent?: string | null; session_id?: string | null } | null } | null;
  const session = snap?.session;
  return {
    live: session?.live === true,
    agent: (session?.agent as string | undefined) ?? null,
    sessionId: (session?.session_id as string | undefined) ?? null,
  };
}

/** What runs in the foreground of a workspace's terminal. */
export type Foreground = 'shell' | 'codex' | 'claude' | 'other' | 'unknown';

const SHELLS = new Set(['zsh', 'bash', 'sh', 'fish', 'dash', 'ksh', 'tcsh', 'csh']);

/** Name tmux (or node-pty) gives the foreground program, as a kind. Claude
 *  Code names its process after its version, e.g. `2.1.299`. */
export function classifyForeground(name: string | null): Foreground {
  if (!name) return 'unknown';
  const base = (name.split('/').pop() ?? '').replace(/^-/, '').toLowerCase();
  if (SHELLS.has(base)) return 'shell';
  if (base === 'codex' || base.startsWith('codex-')) return 'codex';
  if (base === 'claude' || /^\d+\.\d+\.\d+$/.test(base)) return 'claude';
  return 'other';
}

/** How a dispatch reaches a workspace (FEAT-0158, TASK-0660). A live Claude
 *  session is always handed to the sidecar, busy or not, because the cockpit
 *  plugin waits for the session to be idle itself; nothing is typed into it.
 *  Otherwise the terminal's foreground program decides, not the sidecar: a
 *  hook reports a session only once it has run, and Codex's first hook waits
 *  for the first turn, so "no session" does not mean "a shell". */
export function routeFor(
  session: LiveSession, state: string, foreground: Foreground,
): 'submit' | 'queue' | 'repl' | 'shell' | 'hold' {
  if (session.live && session.agent === 'claude' && session.sessionId) return 'submit';
  if (state === 'busy' || state === 'needs-input') return 'queue';
  if (foreground === 'codex') return 'repl';
  if (foreground === 'shell') return 'shell';
  return 'hold';
}

/** Why a dispatch is held, in the words the status line shows. */
function holdReason(workspaceId: string, foreground: Foreground, name: string | null): string {
  if (foreground === 'claude') return 'Claude is running in this terminal but the cockpit cannot reach it — queued';
  if (foreground === 'other' && name) return `${name} is running in this terminal — queued`;
  return hasPty(workspaceId) ? 'could not tell what is running in this terminal — queued' : 'no terminal open — queued';
}

function recordLedger(workspaceId: string, item: DispatchItem): void {
  const base = sidecarUrlFor(workspaceId);
  if (!base) return;
  postJson(`${base}/api/cockpit/dispatch`, {
    // A typed dispatch is stamped when it is written, not when a turn starts;
    // a submitted one is stamped by the sidecar at its turn's start.
    id: item.id, verb: item.verb, agent: item.agent, delivered_by: 'typed',
  });
}

function requeueFront(workspaceId: string, item: DispatchItem): void {
  const q = queueOf(workspaceId);
  q.unshift(item);
  q.splice(QUEUE_MAX);
  persistSoon();
  broadcastQueue(workspaceId);
}

/** Hand a dispatch for a live Claude session to the sidecar, which keeps it
 *  until the cockpit plugin in that session submits it (FEAT-0158). */
async function handToSidecar(
  workspaceId: string, item: DispatchItem, session: LiveSession,
): Promise<ExecuteResult> {
  const base = sidecarUrlFor(workspaceId);
  const res = base
    ? await postJsonResult(`${base}/api/cockpit/deliveries`, { ...item, session_id: session.sessionId })
    : null;
  if (!res || res.status !== 200 || !res.json?.delivery) {
    // The sidecar did not take it: keep it here, and the next state
    // transition tries again. Never fall back to typing it.
    requeueFront(workspaceId, item);
    const why = res?.json?.error ? String(res.json.error) : "the cockpit's server did not answer";
    return { queued: true, warning: `${why} — queued` };
  }
  const delivery = res.json.delivery as Delivery;
  // A dispatch goes to the agent that is running, whatever the Agent menu
  // says (ISS-0321), so that is not worth a warning.
  const warning = delivery.state === 'held' ? `not delivered: ${delivery.reason ?? 'held'}` : undefined;
  return { queued: false, delivered: 'submit', delivery, warning };
}

// ---- delivery state machine ----

interface Terminal { foreground: Foreground; name: string | null }

async function readTerminal(workspaceId: string): Promise<Terminal> {
  const name = await foregroundCommand(workspaceId);
  return { foreground: classifyForeground(name), name };
}

async function deliver(
  workspaceId: string, queued: DispatchItem, state: string,
  known?: LiveSession, knownTerminal?: Terminal,
): Promise<ExecuteResult> {
  const session = known ?? await liveSessionInfo(workspaceId);
  const terminal = knownTerminal ?? await readTerminal(workspaceId);
  const route = routeFor(session, state, terminal.foreground);
  if (route === 'submit') return handToSidecar(workspaceId, queued, session);
  if (route === 'queue' || route === 'hold') {
    requeueFront(workspaceId, queued);
    return route === 'hold'
      ? { queued: true, warning: holdReason(workspaceId, terminal.foreground, terminal.name) }
      : { queued: true };
  }
  const mode: 'shell' | 'repl' = route;
  // A running Codex takes the prompt whatever the Agent menu says, and the
  // ledger names the agent that got it (ISS-0321).
  const item = mode === 'repl' ? { ...queued, agent: 'codex' } : queued;
  const codexRepl = mode === 'repl';
  const data = codexRepl
    ? `\x1b[200~${item.prompt}\x1b[201~`
    : `${item.agent} ${shellEscapeSingle(item.prompt)}\r`;
  if (!writeToPty(workspaceId, data)) {
    // No terminal for this workspace yet — hold in the queue; the next
    // state transition (or terminal open + transition) retries.
    requeueFront(workspaceId, queued);
    return { queued: true, warning: 'no terminal open — queued' };
  }
  if (codexRepl) {
    // Codex treats a burst containing text and Return as pasted input.
    // Finish the paste, let its input loop consume it, then submit separately.
    await new Promise((resolve) => setTimeout(resolve, 200));
    if (!writeToPty(workspaceId, '\r')) {
      // The terminal closed between the paste and its Return, so nothing
      // was submitted. Put the item back rather than drop it (FEAT-0019
      // review, 2026-09-25), exactly as when no terminal is open.
      requeueFront(workspaceId, queued);
      return { queued: true, warning: 'terminal closed before Codex submission — queued again' };
    }
  }
  recordLedger(workspaceId, item);
  broadcast('dispatch:delivered', { workspaceId, item, mode });
  return { queued: false, delivered: mode };
}

export async function executeDispatch(
  workspaceId: string, item: DispatchItem,
): Promise<ExecuteResult> {
  const state = lastKnownState.get(workspaceId) ?? 'idle';
  const session = await liveSessionInfo(workspaceId);
  const terminal = await readTerminal(workspaceId);
  if (routeFor(session, state, terminal.foreground) === 'queue') {
    const q = queueOf(workspaceId);
    q.push(item);
    q.splice(QUEUE_MAX);
    persistSoon();
    broadcastQueue(workspaceId);
    return { queued: true };
  }
  return deliver(workspaceId, item, state, session, terminal);
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
