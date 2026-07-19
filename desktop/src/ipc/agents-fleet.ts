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
  dispatchOrigin?: string;
  queueDepth: number;
  sessionId?: string;
}

export interface FleetPayload { rows: FleetRow[]; generatedAt: number; }

let cache: { at: number; payload: FleetPayload } | null = null;
const CACHE_MS = 3000;

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
    row.agent = sess.agent || row.agent;
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
}
