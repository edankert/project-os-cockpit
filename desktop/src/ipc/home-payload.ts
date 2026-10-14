// What the draft home window is sent, shaped from the sidecar's own payloads
// (FEAT-0160 / TASK-0646).
//
// Kept apart from home-window.ts, and free of any Electron import, so the
// node suite can load the built file and test the shaping without a window.
// Nothing here fetches: it takes what a sidecar answered and trims it.

export interface HomeCriterion { text: string; done: boolean; }

export interface HomePhase {
  key: string;
  title: string;
  status: string;
  rel: string;
  tasks: { done: number; in_progress: number; backlog: number };
  waiting: number;
  features: Array<{ id: string; title: string; status: string; bucket: string }>;
  /** The phase's exit criteria. Null when they were not read, which is not
   *  the same as a phase that has none. */
  exit: HomeCriterion[] | null;
  /** True for the phase the project's own focus names. */
  focus: boolean;
}

export interface HomeRelease {
  id: string;
  version: string;
  status: string;
  rel: string;
  openTests: number;
  toSettle: number;
}

type Loose = Record<string, unknown>;
const asList = (v: unknown): Loose[] => (Array.isArray(v) ? (v as Loose[]) : []);
const num = (v: unknown): number => (typeof v === 'number' && Number.isFinite(v) ? v : 0);

/** The phases a person is in the middle of or has ahead: active and planned.
 *  Finished, deferred and superseded phases are the record, not the status.
 *  The focus phase comes first, then the other active ones, then planned. */
export function trimPhases(stats: Loose | null): HomePhase[] {
  const focusItems = (stats?.focus as Loose | undefined)?.items as Loose | undefined;
  const focusId = String((focusItems?.phase as Loose | undefined)?.id ?? '');
  const phases = asList(stats?.phases)
    .filter((p) => p.status === 'active' || p.status === 'planned')
    .map((p): HomePhase => {
      const tasks = (p.tasks ?? {}) as Loose;
      return {
        key: String(p.key ?? ''),
        title: String(p.title ?? ''),
        status: String(p.status ?? ''),
        rel: String(p.rel ?? ''),
        tasks: { done: num(tasks.done), in_progress: num(tasks.in_progress), backlog: num(tasks.backlog) },
        waiting: num(p.waiting),
        features: asList(p.features).map((f) => ({
          id: String(f.id ?? ''), title: String(f.title ?? ''),
          status: String(f.status ?? ''), bucket: String(f.bucket ?? ''),
        })),
        exit: null,
        focus: !!focusId && String(p.key ?? '') === focusId,
      };
    });
  const rank = (p: HomePhase): number => (p.focus ? 0 : p.status === 'active' ? 1 : 2);
  return phases.sort((a, b) => rank(a) - rank(b) || a.key.localeCompare(b.key));
}

/** One exit criterion as a person reads it: the wikilink brackets and the
 *  "evidence: <...>" tail a phase note carries are for the record. */
export function cleanCriterion(text: string): string {
  return String(text ?? '')
    .replace(/\s+[—-]{1,2}\s+evidence:.*$/is, '')
    .replace(/\[\[([^\]|]+)\|([^\]]+)\]\]/g, '$2')
    .replace(/\[\[([^\]]+)\]\]/g, '$1')
    .trim();
}

/** The exit criteria from a `stats?scope=<phase>` answer. Null when the
 *  answer is missing or is about a different phase. */
export function trimCriteria(scoped: Loose | null, key: string): HomeCriterion[] | null {
  if (!scoped || String((scoped.scope as Loose)?.id ?? '') !== key) return null;
  if (!Array.isArray(scoped.exit_criteria)) return null;
  return asList(scoped.exit_criteria).map((c) => ({ text: cleanCriterion(String(c.text ?? '')), done: c.done === true }));
}

/** A release only while one is being prepared. A shipped release is the
 *  record; a release nobody has started is not something to stand anywhere. */
export function trimRelease(rel: Loose | null): HomeRelease | null {
  if (!rel || !rel.exists || !rel.preparing) return null;
  return {
    id: String(rel.id ?? ''),
    version: String(rel.version ?? ''),
    status: String(rel.status ?? ''),
    rel: String(rel.rel ?? ''),
    openTests: Array.isArray(rel.open_tests) ? rel.open_tests.length : 0,
    toSettle: Array.isArray(rel.settle) ? rel.settle.length : 0,
  };
}
