// Keeps `needs-elsewhere.json` current in every workspace's instrument folder
// (FEAT-0157 / TASK-0671): every 30 seconds while the app runs, and at once
// when a project's sidecar starts or stops. The building and the writing are
// in needs-elsewhere-file.ts and the counting in needs-count.ts; this module
// only gathers the counts and picks the folders.

import { fleetHealth, liveSidecarUrl } from './fleet-health';
import { existingInstrumentDir, instrumentationDisabled } from './agent-instrument';
import { NeedsCount, NeedsCountDeps, needsYouCount } from './needs-count';
import { NEEDS_ELSEWHERE_FILE, elsewherePayload, writeAtomic } from './needs-elsewhere-file';
import { getAllWorkspaces } from './workspaces';

const INTERVAL_MS = 30_000;
const FETCH_MS = 2500;

async function getJson(url: string): Promise<Record<string, unknown> | null> {
  const ctl = new AbortController();
  const timer = setTimeout(() => ctl.abort(), FETCH_MS);
  try {
    const resp = await fetch(url, { signal: ctl.signal });
    if (!resp.ok) return null;
    return (await resp.json()) as Record<string, unknown>;
  } catch {
    return null;
  } finally {
    clearTimeout(timer);
  }
}

/** The counting the home window uses too, with this shell's sources. */
export const shellNeedsDeps: NeedsCountDeps = {
  liveUrl: liveSidecarUrl,
  cold: (id) => fleetHealth().rows.find((r) => r.workspaceId === id)?.digest,
  getJson,
  now: () => Date.now(),
};

let running: Promise<void> | null = null;
let again = false;
let timer: NodeJS.Timeout | null = null;

async function writeAll(): Promise<void> {
  const workspaces = getAllWorkspaces();
  const folders = workspaces
    .map((ws) => ({ ws, dir: existingInstrumentDir(ws.id) }))
    .filter((f): f is { ws: typeof f.ws; dir: string } => f.dir !== null);
  if (!folders.length) return;
  const counts: NeedsCount[] = await Promise.all(workspaces.map((ws) => needsYouCount(ws, shellNeedsDeps)));
  const rows = workspaces.map((ws, i) => ({ id: ws.id, name: ws.name, count: counts[i]! }));
  const now = Date.now();
  for (const { ws, dir } of folders) {
    try {
      writeAtomic(dir, NEEDS_ELSEWHERE_FILE, JSON.stringify(elsewherePayload(ws.id, rows, now), null, 2) + '\n');
    } catch (err) {
      console.error(`[needs-elsewhere] write failed for ${ws.id}:`, err);
    }
  }
}

/** Rewrites every folder's file now. One pass at a time; a call that arrives
 *  during one makes it run once more. Never throws. */
export function refreshNeedsElsewhere(): void {
  if (instrumentationDisabled()) return;
  if (running) { again = true; return; }
  running = (async () => {
    do {
      again = false;
      await writeAll().catch((err) => console.error('[needs-elsewhere] pass failed:', err));
    } while (again);
  })().finally(() => { running = null; });
}

/** Starts the 30-second refresh, with a first pass now. */
export function startNeedsElsewhere(): void {
  if (instrumentationDisabled() || timer) return;
  refreshNeedsElsewhere();
  timer = setInterval(refreshNeedsElsewhere, INTERVAL_MS);
  timer.unref?.();
}
