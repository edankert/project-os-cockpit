// Fleet state proxy (FEAT-0032 / TASK-0150).
//
// The ~agents screen needs rich agent data for EVERY workspace, but the
// renderer only holds a live SSE connection to the active one. This
// module runs in main — where the poller's cross-workspace state, the
// per-workspace sidecar URLs, and the dispatch queues all live — and
// assembles one row per workspace: coarse state (poller) plus, when a
// sidecar is live, its /api/cockpit/state session/cost/queue. A short
// cache keeps a polling ~agents page from hammering the sidecars.

import { ipcMain } from 'electron';
import * as fs from 'node:fs';
import * as path from 'node:path';

import { getAllWorkspaces } from './workspaces';
import { getLastAgentPayloads } from './agent-state-poller';
import { sidecarUrlFor } from './sidecar';
import { queueDepthFor } from './dispatch-queue';

export interface FleetRow {
  workspaceId: string;
  name: string;
  root: string;
  state: string | null;
  message?: string;
  stateTs?: string;
  live: boolean;
  agent?: string;
  lastPrompt?: string;
  lastFile?: string;
  undocumented?: boolean;
  cost?: number;
  ctx?: number;
  fiveHourPct?: number;
  fiveHourResetsAt?: string;
  // Full account-global usage reading + when it was captured — the
  // renderer keeps the freshest across workspaces (TASK-0169).
  rateLimits?: Record<string, { used_percentage: number; resets_at?: string }>;
  rateLimitsAt?: string;
  dispatchOrigin?: string;
  queueDepth: number;
  sessionId?: string;
}

export interface FleetPayload { rows: FleetRow[]; generatedAt: number; }

let cache: { at: number; payload: FleetPayload } | null = null;
const CACHE_MS = 3000;
// Per-workspace session-list cache (TASK-0180) — smooths the ~agents
// session section's rebuilds on bursty agent-state events.
const sessionsCache = new Map<string, { at: number; data: unknown[] }>();
const SESSIONS_CACHE_MS = 3000;

async function fetchState(url: string): Promise<Record<string, unknown> | null> {
  const ctl = new AbortController();
  const timer = setTimeout(() => ctl.abort(), 900);
  try {
    const resp = await fetch(`${url}/api/cockpit/state`, { signal: ctl.signal });
    if (!resp.ok) return null;
    return (await resp.json()) as Record<string, unknown>;
  } catch {
    return null; // sidecar slow / down — coarse row only
  } finally {
    clearTimeout(timer);
  }
}

async function buildRow(ws: { id: string; name: string; root: string }): Promise<FleetRow> {
  const payload = getLastAgentPayloads().get(ws.id) ?? null;
  const row: FleetRow = {
    workspaceId: ws.id,
    name: ws.name,
    root: ws.root,
    state: payload?.state ?? null,
    message: payload?.message,
    stateTs: payload?.ts,
    agent: payload?.agent,
    live: false,
    queueDepth: queueDepthFor(ws.id),
  };
  const url = sidecarUrlFor(ws.id);
  if (!url) return row;
  const snap = await fetchState(url);
  if (!snap) return row;
  const activity = snap.activity as { state?: string } | null | undefined;
  const liveSession = snap.session as Record<string, any> | null | undefined;
  const sess = liveSession ?? (snap.last_session as Record<string, any> | null | undefined);
  if (sess) {
    row.live = Boolean(liveSession);
    // Prefer the live agent (poller/agent-state, set on the base row)
    // over a stale last_session agent — otherwise a one-off codex run
    // relabels a claude workspace (ISS-0012). A genuinely live session's
    // agent still wins.
    if (liveSession || !row.agent) row.agent = sess.agent || row.agent;
    row.lastPrompt = sess.last_prompt || undefined;
    row.undocumented = Boolean(sess.undocumented);
    row.sessionId = sess.session_id;
    const files = sess.files as string[] | undefined;
    if (files && files.length) {
      const f = files[files.length - 1];
      row.lastFile = f.split('/').pop() || f;
    }
    const cost = sess.cost as Record<string, any> | null | undefined;
    if (cost) {
      if (typeof cost.total_cost_usd === 'number') row.cost = cost.total_cost_usd;
      if (typeof cost.used_percentage === 'number') row.ctx = cost.used_percentage;
      const rl = cost.rate_limits?.five_hour;
      if (rl && typeof rl.used_percentage === 'number') {
        row.fiveHourPct = rl.used_percentage;
        // resets_at is normalised to an ISO string at ingest (F2).
        if (typeof rl.resets_at === 'string') row.fiveHourResetsAt = rl.resets_at;
      }
    }
    const dispatches = sess.dispatches as Array<{ verb?: string; id?: string }> | undefined;
    if (dispatches && dispatches.length) {
      const d = dispatches[dispatches.length - 1];
      row.dispatchOrigin = `${d.verb || 'run'} ${d.id || ''}`.trim();
    }
  }
  // Account-global usage: the snapshot's freshest reading across ALL of
  // this workspace's sessions, not just the live/last one (TASK-0171).
  const topRl = snap.rate_limits as FleetRow['rateLimits'] | undefined;
  const topAt = snap.rate_limits_at as string | undefined;
  if (topRl && typeof topRl === 'object' && typeof topAt === 'string') {
    row.rateLimits = topRl;
    row.rateLimitsAt = topAt;
  }
  if (row.live && activity?.state) row.state = activity.state;
  return row;
}

export function registerAgentsFleetIpc(): void {
  ipcMain.handle('agents:fleet', async (): Promise<FleetPayload> => {
    const now = Date.now();
    if (cache && now - cache.at < CACHE_MS) return cache.payload;
    const rows = await Promise.all(getAllWorkspaces().map(buildRow));
    const payload: FleetPayload = { rows, generatedAt: now };
    cache = { at: now, payload };
    return payload;
  });

  // Session history for ONE workspace (TASK-0180 / ISS-0013): from its
  // live sidecar when up, else the persisted `.cockpit/sessions.json` so
  // the ~agents screen can show history for any project, even one whose
  // sidecar isn't running.
  ipcMain.handle('agents:sessions', async (_evt, workspaceId: string): Promise<unknown[]> => {
    // Short per-workspace cache — the ~agents screen rebuilds its
    // session section on every agent-state event, so cache prevents a
    // bursty refetch/flicker during peer-workspace activity.
    const now = Date.now();
    const hit = sessionsCache.get(workspaceId);
    if (hit && now - hit.at < SESSIONS_CACHE_MS) return hit.data;
    const compute = async (): Promise<unknown[]> => {
      const ws = getAllWorkspaces().find((w) => w.id === workspaceId);
      if (!ws) return [];
      const url = sidecarUrlFor(workspaceId);
      if (url) {
        try {
          const ctl = new AbortController();
          const timer = setTimeout(() => ctl.abort(), 2500);
          const resp = await fetch(`${url}/api/cockpit/sessions`, { signal: ctl.signal });
          clearTimeout(timer);
          if (resp.ok) {
            const data = (await resp.json()) as { sessions?: unknown[] };
            if (Array.isArray(data.sessions)) return data.sessions;
          }
        } catch { /* sidecar down/slow — fall through to the file */ }
      }
      try {
        const raw = await fs.promises.readFile(
          path.join(ws.root, '.cockpit', 'sessions.json'), 'utf-8');
        const data = JSON.parse(raw) as { sessions?: unknown[] };
        return Array.isArray(data.sessions) ? data.sessions : [];
      } catch { return []; }
    };
    const data = await compute();
    sessionsCache.set(workspaceId, { at: now, data });
    return data;
  });
}
