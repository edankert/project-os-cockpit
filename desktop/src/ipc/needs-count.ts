// How many things need the person in one project (FEAT-0157 / TASK-0671).
//
// One function, used by the draft home window and by the file each cockpit
// terminal's Claude plugin reads for the other projects' count, so the two
// can never say different numbers for the same project. It imports nothing
// from Electron, so the node suite runs it as built.
//
// A count is live when the project's sidecar answers, cold when no sidecar
// runs and the last fleet pass counted it, and unknown otherwise. An unknown
// count is null, never 0: a project nobody read does not owe nothing.

export type NeedsSource = 'live' | 'cold' | 'unknown';

export interface NeedsCount {
  count: number | null;
  /** When the count was taken, as an ISO time; null when unknown. */
  asOf: string | null;
  source: NeedsSource;
}

export interface ColdDigest { needsYou: number; computedAt: string }

export interface NeedsCountDeps {
  /** The project's live sidecar, or null when none answers. */
  liveUrl: (ws: { id: string; root: string }) => Promise<string | null>;
  /** The last cold pass's digest for the workspace, if it ran. */
  cold: (workspaceId: string) => ColdDigest | null | undefined;
  getJson: (url: string) => Promise<Record<string, unknown> | null>;
  now: () => number;
}

export const UNKNOWN: NeedsCount = { count: null, asOf: null, source: 'unknown' };

/** The cold pass's count with its date, or unknown when it never ran. */
export function coldCount(digest: ColdDigest | null | undefined): NeedsCount {
  if (!digest || !Number.isFinite(digest.needsYou)) return UNKNOWN;
  return { count: digest.needsYou, asOf: digest.computedAt || null, source: 'cold' };
}

/** The count from a live sidecar's obligations answer: its `total`, which is
 *  the number the badges show (ADR-0020 decision 3). Unknown when the answer
 *  is missing or carries no total. */
export function liveCount(obligations: Record<string, unknown> | null, now: number): NeedsCount {
  const total = Number(obligations?.total);
  if (!obligations || obligations.total === undefined || !Number.isFinite(total)) return UNKNOWN;
  return { count: total, asOf: new Date(now).toISOString(), source: 'live' };
}

/** One project's count: live when its sidecar runs, cold when none does.
 *  A sidecar that runs and does not answer is unknown, as the home window
 *  says "not read" for it. */
export async function needsYouCount(
  ws: { id: string; root: string }, deps: NeedsCountDeps,
): Promise<NeedsCount> {
  const base = await deps.liveUrl(ws);
  if (!base) return coldCount(deps.cold(ws.id));
  return liveCount(await deps.getJson(`${base}/api/cockpit/obligations`), deps.now());
}
