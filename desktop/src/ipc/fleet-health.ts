// Fleet health — validator state for every discovered workspace
// (FEAT-0028 / TASK-0248).
//
// FEAT-0018 made verification drift visible for the repo you are
// browsing. This module fans that signal in across the fleet: one row
// per discovered workspace, so drift anywhere is visible without
// opening each project.
//
// LIVE workspaces only, here. Each running sidecar already exposes
// `GET /api/cockpit/validation` and publishes `cockpit:validation` on
// its SSE channel when the observable state changes, so this costs one
// fetch at subscribe time and nothing afterwards — no polling. Cold
// workspaces (discovered, no sidecar) are TASK-0249's problem and show
// as `unknown` until it lands.
//
// A sidecar is "live" if EITHER this app spawned it (the sidecars map)
// OR the workspace carries a `.cockpit/url` that answers identity with
// a matching root — a standalone `project-os-cockpit` in a terminal is
// just as live, and the ~agents screen already treats it that way.
//
// The identity check is not optional. `.cockpit/url` files survive an
// unclean exit pointing at a port another workspace's sidecar may claim
// next launch (ISS-0007) — main.ts's janitor exists for exactly that.
// Trusting the file would attribute one repo's drift to another, and a
// badge on the wrong repo is worse than no badge.

import { ipcMain, BrowserWindow } from 'electron';
import * as fsp from 'node:fs/promises';
import { execFile } from 'node:child_process';
import * as http from 'node:http';
import * as path from 'node:path';

import { getAllWorkspaces } from './workspaces';
import { sidecarUrlFor, pythonExecutable } from './sidecar';
import type { Workspace } from '../types';

type WorkspacesGetter = () => Workspace[];

// Injected, following startAgentStatePoller's shape — the poller takes
// its workspace list the same way. Defaulted so nothing breaks if the
// module is used before registration.
let getWorkspaces: WorkspacesGetter = () => getAllWorkspaces();

/** Validator state for one workspace.
 *
 *  `unknown` is a first-class value, not a placeholder: a repo nobody
 *  has checked must never be presentable as a repo that passed.
 */
export type HealthState = 'ok' | 'failing' | 'unavailable' | 'unknown';

export interface HealthRow {
  workspaceId: string;
  name: string;
  root: string;
  state: HealthState;
  errors: number;
  warnings: number;
  /** ISO timestamp from the SIDECAR's report, never stamped on receipt —
   *  re-stamping would make a cached report look freshly checked. */
  checkedAt: string | null;
  /** How the state was obtained. null when `unknown`. */
  source: 'live' | 'cold' | null;
  /** The validator's own explanation when `unavailable`. */
  detail?: string;
  /** A cold reading older than the schedule that produced it. Live
   *  rows are never stale — their sidecar pushes on change. */
  stale?: boolean;
}

export interface FleetHealthPayload {
  rows: HealthRow[];
  generatedAt: number;
}

interface Subscription {
  url: string;
  request: http.ClientRequest;
}

/** workspaceId → last known validator state. */
const health = new Map<string, HealthRow>();
/** workspaceId → live SSE subscription. */
const subs = new Map<string, Subscription>();

let notify: (() => void) | null = null;

function emptyRow(ws: { id: string; name: string; root: string }): HealthRow {
  return {
    workspaceId: ws.id,
    name: ws.name,
    root: ws.root,
    state: 'unknown',
    errors: 0,
    warnings: 0,
    checkedAt: null,
    source: null,
  };
}

/** Fold a sidecar's `/api/cockpit/validation` payload into a row. */
export function rowFromReport(
  ws: { id: string; name: string; root: string },
  report: Record<string, unknown>,
  source: 'live' | 'cold',
): HealthRow {
  const raw = String(report.state ?? '');
  const state: HealthState =
    raw === 'ok' || raw === 'failing' || raw === 'unavailable' ? raw : 'unknown';
  const errors = Array.isArray(report.errors) ? report.errors.length : 0;
  const warnings = Array.isArray(report.warnings) ? report.warnings.length : 0;
  const row: HealthRow = {
    workspaceId: ws.id,
    name: ws.name,
    root: ws.root,
    state,
    errors,
    warnings,
    checkedAt: typeof report.checked_at === 'string' ? report.checked_at : null,
    source: state === 'unknown' ? null : source,
  };
  if (typeof report.detail === 'string') row.detail = report.detail;
  return row;
}

/** The live sidecar URL for a workspace, or null.
 *
 *  In-app sidecars are authoritative (we spawned them, we know the
 *  root). An external `.cockpit/url` is trusted only after it answers
 *  `/api/cockpit/identity` with a root matching the workspace — the
 *  same check main.ts's janitor makes before unlinking one.
 */
export async function liveSidecarUrl(ws: { id: string; root: string }): Promise<string | null> {
  const own = sidecarUrlFor(ws.id);
  if (own) return own;

  let url: string;
  try {
    url = (await fsp.readFile(path.join(ws.root, '.cockpit', 'url'), 'utf-8')).trim();
  } catch {
    return null;
  }
  if (!/^https?:\/\/(127\.0\.0\.1|localhost)[:/]/.test(url)) return null;
  try {
    const ctl = new AbortController();
    const timer = setTimeout(() => ctl.abort(), 800);
    const resp = await fetch(`${url}/api/cockpit/identity`, { signal: ctl.signal });
    clearTimeout(timer);
    if (!resp.ok) return null;
    const identity = (await resp.json()) as { root?: string };
    let wsRoot = ws.root;
    try { wsRoot = await fsp.realpath(ws.root); } catch { /* keep raw */ }
    // Wrong root means this url belongs to a DIFFERENT workspace's
    // sidecar. Reporting its drift here would blame the wrong repo.
    if ((identity.root ?? '').toLowerCase() !== wsRoot.toLowerCase()) return null;
    return url;
  } catch {
    return null;
  }
}

async function fetchValidation(url: string): Promise<Record<string, unknown> | null> {
  try {
    const ctl = new AbortController();
    const timer = setTimeout(() => ctl.abort(), 2500);
    const resp = await fetch(`${url}/api/cockpit/validation`, { signal: ctl.signal });
    clearTimeout(timer);
    if (!resp.ok) return null;
    return (await resp.json()) as Record<string, unknown>;
  } catch {
    return null;
  }
}

/** Drop a workspace's LIVE state back to `unknown`, tearing down its
 *  subscription.
 *
 *  Deliberately NOT "keep the last value": a dead sidecar's last report
 *  is a claim about a repo nobody is watching any more, and it would
 *  age silently into a lie. Grey is the honest answer.
 *
 *  A `cold` row is left alone — TASK-0249 owns those, and they have
 *  their own staleness marking.
 */
function degrade(workspaceId: string): void {
  const sub = subs.get(workspaceId);
  if (sub) {
    subs.delete(workspaceId);
    try { sub.request.destroy(); } catch { /* already gone */ }
  }
  const existing = health.get(workspaceId);
  if (existing && existing.source === 'live') {
    health.set(workspaceId, {
      ...existing, state: 'unknown', source: null, errors: 0, warnings: 0, checkedAt: null,
    });
    notify?.();
  }
}

/** Subscribe to one sidecar's `cockpit:validation` stream.
 *
 *  Same SSE line protocol as agent-focus.ts. Kept separate rather than
 *  shared because that module's subscription is keyed by WINDOW and
 *  tied to window lifecycle; this one is keyed by workspace and
 *  outlives any window.
 */
function subscribe(ws: { id: string; name: string; root: string }, url: string): void {
  if (subs.get(ws.id)?.url === url) return;
  degrade(ws.id);

  const parsed = new URL(url);
  const req = http.get({
    host: parsed.hostname,
    port: parsed.port ? Number(parsed.port) : 80,
    path: '/_events',
    headers: { Accept: 'text/event-stream' },
  }, (res) => {
    if (res.statusCode !== 200) { res.resume(); degrade(ws.id); return; }
    res.setEncoding('utf-8');
    let buffer = '';
    let currentEvent = '';
    let currentData = '';

    const handleEvent = (): void => {
      if (currentEvent === 'cockpit:validation') {
        try {
          const report = JSON.parse(currentData) as Record<string, unknown>;
          health.set(ws.id, rowFromReport(ws, report, 'live'));
          notify?.();
        } catch { /* malformed frame — keep the last good row */ }
      }
      currentEvent = '';
      currentData = '';
    };

    res.on('data', (chunk: string) => {
      buffer += chunk;
      let nl: number;
      while ((nl = buffer.indexOf('\n')) >= 0) {
        const line = buffer.slice(0, nl);
        buffer = buffer.slice(nl + 1);
        if (line === '') { handleEvent(); continue; }
        if (line.startsWith(':')) continue; // heartbeat
        if (line.startsWith('event: ')) {
          currentEvent = line.slice('event: '.length).trim();
        } else if (line.startsWith('data: ')) {
          currentData = currentData
            ? `${currentData}\n${line.slice('data: '.length)}`
            : line.slice('data: '.length);
        }
      }
    });

    res.on('end', () => degrade(ws.id));
    res.on('error', () => degrade(ws.id));
  });
  req.on('error', () => degrade(ws.id));

  subs.set(ws.id, { url, request: req });
}

/** Reconcile subscriptions with the current workspace list.
 *
 *  Called on a slow interval and on demand. The SSE stream carries the
 *  updates; this only notices sidecars that appeared or vanished.
 */
export async function refreshLiveWorkspaces(): Promise<void> {
  const workspaces = getWorkspaces();
  const seen = new Set<string>();
  await Promise.all(workspaces.map(async (ws) => {
    seen.add(ws.id);
    if (!health.has(ws.id)) health.set(ws.id, emptyRow(ws));
    const url = await liveSidecarUrl(ws);
    if (!url) { degrade(ws.id); return; }
    const fresh = subs.get(ws.id)?.url !== url;
    subscribe(ws, url);
    // One fetch at subscribe time: the SSE event only fires on CHANGE,
    // so a repo that has been quietly failing since before we connected
    // would otherwise sit at `unknown` indefinitely.
    if (fresh) {
      const report = await fetchValidation(url);
      if (report) { health.set(ws.id, rowFromReport(ws, report, 'live')); notify?.(); }
    }
  }));
  // A workspace removed from the list should not linger.
  for (const id of Array.from(health.keys())) {
    if (!seen.has(id)) { degrade(id); health.delete(id); }
  }
}

// ---- cold workspaces (TASK-0249) ----------------------------------
//
// A discovered repo with no sidecar still has a validator state, and
// leaving it `unknown` forever would make the fleet surface answer
// "I don't know" for most of the fleet most of the time.
//
// The cost is real and the bounds are deliberate:
//   * ONE subprocess for the whole batch, serial inside Python — ten
//     validators at once is a visible stall on the machine the user is
//     working on, and nobody is waiting on a repo nobody has open.
//   * A slow interval, because a repo nobody is editing does not drift.
//   * Skipped entirely for workspaces with a live sidecar; they have a
//     better answer already.
//
// This runs a script in repositories this app does not own, so
// read-only is asserted by a test rather than promised in a comment.
// The validator's single write path (`fix_metrics`) is behind
// `--fix-metrics`, which is why COLD_ARGV must never grow it.

export const COLD_INTERVAL_MS = 10 * 60_000;
/** A cold reading older than this is presented as stale, not current. */
export const COLD_STALE_AFTER_MS = 2 * COLD_INTERVAL_MS;
const COLD_TIMEOUT_MS = 120_000;

/** The exact argv for the cold pass. Exported so a guard can assert
 *  what this spawns in other people's repositories. */
export function coldArgv(roots: string[]): string[] {
  return ['-m', 'project_os_cockpit.fleet_validate', ...roots];
}

interface ColdLine {
  root: string;
  state?: string;
  errors?: number;
  warnings?: number;
  checked_at?: string | null;
  detail?: string;
}

function runColdValidator(roots: string[]): Promise<ColdLine[]> {
  return new Promise((resolve) => {
    execFile(
      pythonExecutable(),
      coldArgv(roots),
      { timeout: COLD_TIMEOUT_MS, maxBuffer: 4 * 1024 * 1024 },
      (_err, stdout) => {
        const out: ColdLine[] = [];
        for (const line of (stdout || '').split('\n')) {
          if (!line.trim()) continue;
          try { out.push(JSON.parse(line) as ColdLine); } catch { /* skip */ }
        }
        resolve(out);
      },
    );
  });
}

/** Validate every discovered workspace that has no live sidecar. */
export async function refreshColdWorkspaces(): Promise<void> {
  const cold = getWorkspaces().filter((ws) => !subs.has(ws.id));
  if (!cold.length) return;
  const byRoot = new Map(cold.map((ws) => [ws.root, ws]));
  const lines = await runColdValidator(cold.map((ws) => ws.root));
  for (const line of lines) {
    const ws = byRoot.get(line.root);
    if (!ws) continue;
    // A workspace whose sidecar came up while the batch ran has a
    // better answer now; do not overwrite it with the older one.
    if (subs.has(ws.id)) continue;
    health.set(ws.id, rowFromReport(ws, {
      state: line.state,
      errors: new Array(line.errors ?? 0),
      warnings: new Array(line.warnings ?? 0),
      checked_at: line.checked_at ?? undefined,
      detail: line.detail,
    }, 'cold'));
  }
  notify?.();
}

/** Age a cold row past its schedule into `stale`.
 *
 *  Presenting a two-hour-old reading as current is the failure this
 *  exists to avoid — the row keeps its state and count, but says how
 *  old it is.
 */
export function markStale(rows: HealthRow[], now: number): HealthRow[] {
  return rows.map((row) => {
    if (row.source !== 'cold' || !row.checkedAt) return row;
    const age = now - Date.parse(row.checkedAt);
    return Number.isFinite(age) && age > COLD_STALE_AFTER_MS
      ? { ...row, stale: true }
      : row;
  });
}

/** Current fleet health, one row per discovered workspace. */
export function fleetHealth(): FleetHealthPayload {
  const now = Date.now();
  const rows = markStale(
    getWorkspaces().map((ws) => health.get(ws.id) ?? emptyRow(ws)), now);
  return { rows, generatedAt: now };
}

/** Record a row obtained some other way (TASK-0249's cold path). */
export function setHealthRow(row: HealthRow): void {
  health.set(row.workspaceId, row);
  notify?.();
}

/** Whether a workspace currently has a live subscription. */
export function hasLiveSubscription(workspaceId: string): boolean {
  return subs.has(workspaceId);
}

/** Test seam — inject the workspace list and a change callback, and
 *  reset module state between cases. Registration goes through
 *  `registerFleetHealthIpc`; this exists so the behaviour above can be
 *  exercised without an Electron main process. */
export function __configureFleetHealth(
  workspaces: WorkspacesGetter,
  onChange?: () => void,
): void {
  getWorkspaces = workspaces;
  notify = onChange ?? null;
}

/** Test seam — reset module state between cases. */
export function __resetFleetHealth(): void {
  for (const id of Array.from(subs.keys())) {
    const sub = subs.get(id);
    subs.delete(id);
    try { sub?.request.destroy(); } catch { /* ignore */ }
  }
  health.clear();
}

const RECONCILE_MS = 30_000;
let reconcileTimer: NodeJS.Timeout | null = null;
let coldTimer: NodeJS.Timeout | null = null;

interface FleetHealthDeps {
  getAllWindows: () => BrowserWindow[];
  getWorkspaces?: WorkspacesGetter;
}

export function registerFleetHealthIpc(deps: FleetHealthDeps): void {
  if (deps.getWorkspaces) getWorkspaces = deps.getWorkspaces;
  notify = () => {
    const payload = fleetHealth();
    for (const win of deps.getAllWindows()) {
      if (!win.isDestroyed()) win.webContents.send('fleet:health', payload);
    }
  };

  ipcMain.handle('fleet:health', async (): Promise<FleetHealthPayload> => {
    // Live only: cheap, and the cold pass is on its own schedule. A
    // surface opening must not trigger ten subprocesses.
    await refreshLiveWorkspaces();
    return fleetHealth();
  });

  // Explicit re-check, for a surface that offers one. Still bounded by
  // the same single-subprocess batch.
  ipcMain.handle('fleet:health-recheck', async (): Promise<FleetHealthPayload> => {
    await refreshLiveWorkspaces();
    await refreshColdWorkspaces();
    return fleetHealth();
  });

  if (reconcileTimer) clearInterval(reconcileTimer);
  reconcileTimer = setInterval(() => { void refreshLiveWorkspaces(); }, RECONCILE_MS);
  reconcileTimer.unref?.();

  if (coldTimer) clearInterval(coldTimer);
  coldTimer = setInterval(() => { void refreshColdWorkspaces(); }, COLD_INTERVAL_MS);
  coldTimer.unref?.();

  // Delayed, for the reason main.ts's janitor is delayed: at
  // `app.whenReady` the renderer has not asked for the workspace list
  // yet, so discovery is empty and a pass here validates nothing —
  // leaving every repo `unknown` until the 10-minute timer. Measured:
  // without this, the first cold pass returned zero rows and the rail
  // stayed blank until a manual re-check.
  //
  // Live first, then cold — the live pass populates subscriptions and
  // the cold pass skips whatever it claimed. The other order would
  // validate repos that were about to answer for themselves.
  setTimeout(() => {
    void refreshLiveWorkspaces().then(() => refreshColdWorkspaces());
  }, 4000);
}

export function stopFleetHealth(): void {
  if (reconcileTimer) { clearInterval(reconcileTimer); reconcileTimer = null; }
  if (coldTimer) { clearInterval(coldTimer); coldTimer = null; }
  for (const id of Array.from(subs.keys())) degrade(id);
}
