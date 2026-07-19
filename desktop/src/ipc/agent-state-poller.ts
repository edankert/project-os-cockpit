// Per-workspace agent-state poller (FEAT-0010 / TASK-0082).
//
// Every workspace cockpit (mode 1 or mode 3) writes its current
// agent-state to `<project-root>/.cockpit/agent-state.json` on every
// transition (FEAT-0013 / TASK-0081). This module polls those files
// across all discovered workspaces and fans changes to the renderer,
// so the workspace rail can paint per-workspace status dots without
// keeping a live HTTP/SSE connection per workspace.
//
// Polling, not fs.watch: fs.watch on a directory shared with editors
// is noisy (atomic-write swaps fire ENOENT briefly), and the state
// files change at most every few seconds — polling is cheap and
// resilient.
//
// TASK-0087 adds OS notification on transition INTO `waiting` —
// edge-triggered (not retriggered every poll), suppressed when the
// user is already looking at that workspace, click brings the
// window forward + sends `workspaces:switch-to`.

import { BrowserWindow, Notification } from 'electron';

import { onAgentStateChanged } from './dispatch-queue';
import * as fs from 'node:fs/promises';
import * as path from 'node:path';

import type { Workspace } from '../types';

interface AgentStatePayload {
  state: string;
  ts: string;
  target?: string;
  agent?: string;
  message?: string;
  decayed_from?: string;
}

type WorkspacesGetter = () => Workspace[];
type WindowGetter = () => BrowserWindow | null;
type AllWindowsGetter = () => BrowserWindow[];
type ActiveIdGetter = () => string | null;

let pollTimer: NodeJS.Timeout | null = null;
const lastSerialised = new Map<string, string>(); // workspaceId → JSON
const lastState = new Map<string, string>();      // workspaceId → state name
const lastPayload = new Map<string, AgentStatePayload>(); // decayed payload

/** Latest (decay-applied) agent-state payload per workspace — the
 * coarse cross-workspace data the fleet view reads (TASK-0150). */
export function getLastAgentPayloads(): ReadonlyMap<string, AgentStatePayload> {
  return lastPayload;
}

const POLL_INTERVAL_MS = 5_000;
// Poller-side decay (FEAT-0027 / TASK-0143): sidecar-owned state
// decays server-side, but external-hook state for sidecar-less
// workspaces has no owner — treat stale attention states as idle.
// Unified with the sidecar's own decay window (TASK-0154): both read
// COCKPIT_AGENT_STATE_DECAY_SECONDS so a single override can't leave
// the two decay clocks disagreeing.
const DECAY_SECONDS = Number(process.env.COCKPIT_AGENT_STATE_DECAY_SECONDS) || 600;
const DECAY_MS = DECAY_SECONDS * 1_000;
const DECAYABLE = new Set(['busy', 'waiting', 'needs-input']);

function applyDecay(payload: AgentStatePayload | null): AgentStatePayload | null {
  if (!payload || !DECAYABLE.has(payload.state)) return payload;
  const ts = Date.parse(payload.ts);
  if (!Number.isFinite(ts) || Date.now() - ts <= DECAY_MS) return payload;
  return { state: 'idle', ts: payload.ts, decayed_from: payload.state };
}

interface PollerDeps {
  getWorkspaces: WorkspacesGetter;
  getWindow: WindowGetter;
  /** All open BrowserWindows — multi-window support (TASK-0092).
   * If omitted, falls back to `getWindow()` only. */
  getAllWindows?: AllWindowsGetter;
  getActiveWorkspaceId: ActiveIdGetter;
}

let deps: PollerDeps | null = null;

export function startAgentStatePoller(d: PollerDeps): void {
  stopAgentStatePoller();
  deps = d;
  pollTimer = setInterval(() => { void tick(); }, POLL_INTERVAL_MS);
  // Fire one immediate tick so the rail's dots populate on first paint
  // without waiting 5 s. (Skip notifications on this primer pass — we
  // shouldn't ping the user about state that's been sitting there
  // since before the app launched.)
  void tick({ primer: true });
}

/** Last-known agent state per workspace (quit guard, TASK-0145). */
export function getLastAgentStates(): ReadonlyMap<string, string> {
  return lastState;
}

export function stopAgentStatePoller(): void {
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
  lastSerialised.clear();
  lastState.clear();
  deps = null;
}

async function tick(opts: { primer?: boolean } = {}): Promise<void> {
  if (!deps) return;
  const workspaces = deps.getWorkspaces();
  const focused = deps.getWindow();
  const windows = deps.getAllWindows ? deps.getAllWindows() : (focused ? [focused] : []);
  const liveWindows = windows.filter((w) => !w.isDestroyed());
  if (liveWindows.length === 0) return;

  for (const ws of workspaces) {
    const file = path.join(ws.root, '.cockpit', 'agent-state.json');
    let payload: AgentStatePayload | null = null;
    try {
      const raw = await fs.readFile(file, 'utf-8');
      const parsed = JSON.parse(raw);
      if (parsed && typeof parsed === 'object' && typeof parsed.state === 'string') {
        payload = parsed as AgentStatePayload;
      }
    } catch {
      payload = null;
    }
    payload = applyDecay(payload);
    // Diff against the last serialised form so unchanged files don't
    // spam IPC every 5 s.
    const serialised = payload ? JSON.stringify(payload) : '';
    const prev = lastSerialised.get(ws.id);
    if (prev === serialised) continue;
    lastSerialised.set(ws.id, serialised);
    if (payload) lastPayload.set(ws.id, payload); else lastPayload.delete(ws.id);
    // Fan to every open window so all rails update.
    for (const w of liveWindows) {
      w.webContents.send('workspaces:agent-state', {
        workspaceId: ws.id,
        payload,
      });
    }

    // TASK-0087 — fire OS notification on transition INTO `waiting`.
    const newState = payload?.state ?? '';
    const prevState = lastState.get(ws.id) ?? '';
    lastState.set(ws.id, newState);
    // Feed the dispatch-queue runtime (FEAT-0025) — delivery happens
    // in main so background workspaces get their queued work too.
    onAgentStateChanged(ws.id, newState, { deliver: !opts.primer });
    const notifiable = newState === 'waiting' || newState === 'needs-input';
    const wasNotifiable = prevState === 'waiting' || prevState === 'needs-input';
    if (!opts.primer && notifiable && !wasNotifiable) {
      // Notification belongs to the most-recently-focused window
      // (so the user only gets one chime, not N).
      const owner = focused && !focused.isDestroyed() ? focused : liveWindows[0];
      maybeNotifyWaiting(ws, payload!, owner);
    }
  }
}

function maybeNotifyWaiting(
  ws: Workspace,
  payload: AgentStatePayload,
  window: BrowserWindow,
): void {
  // Suppress when the user is already staring at this workspace —
  // the rail dot is already lit; the chime is just noise.
  const activeId = deps?.getActiveWorkspaceId() ?? null;
  if (window.isFocused() && activeId === ws.id) return;

  if (!Notification.isSupported()) return;

  const body = payload.message
    ? `${payload.message}`
    : payload.state === 'needs-input'
      ? 'agent needs your input'
      : 'agent is waiting for input';
  const notification = new Notification({
    title: `Cockpit · ${ws.name}`,
    body,
    silent: false,
  });
  notification.on('click', () => {
    if (window.isDestroyed()) return;
    if (window.isMinimized()) window.restore();
    window.show();
    window.focus();
    window.webContents.send('workspaces:switch-to', { workspaceId: ws.id });
  });
  notification.show();
}
