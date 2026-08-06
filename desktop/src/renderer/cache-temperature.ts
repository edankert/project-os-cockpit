// Whether a workspace's session has gone cold, as a pure function
// (FEAT-0081 / TASK-0346, ISS-0105).
//
// Split out for the reason `health-marks.ts` was: the behaviour that
// matters here is a TRANSITION over time, and a guard shaped like
// `assert 'cold' in source` passes just as happily when the transition
// never fires. Given a clock as an argument, the boundary can be tested
// at T+59min and T+61min without a DOM, a timer, or a running app.
//
// Like `health-marks.ts` this file deliberately declares no imports and
// no exports: `renderer.ts` is loaded as a plain `<script>`, so this is
// loaded the same way and `cacheTemperature` becomes a global. The node
// suite reads the built file and evaluates it, which is why the shape
// matters.

/** Prompt-cache TTL these sessions are written under, in ms.
 *
 *  Matches `session_cache.TTL_1H` on the Python side. Duplicated rather
 *  than served because the rail must decide for TEN workspaces without
 *  ten sidecar round-trips — and because the value has to be available
 *  when a sidecar is not running at all.
 */
const CACHE_TTL_MS = 60 * 60 * 1000;

interface TemperatureInput {
  /** Last agent-state timestamp for the workspace (ISO 8601). */
  ts?: string | null;
  /** Current agent state. */
  state?: string | null;
}

/** `warm`, `cold`, or `unknown` when there is no usable timestamp.
 *
 *  `unknown` is not `cold`: a square with no timestamp has told us
 *  nothing, and painting it grey would assert an age we never measured.
 *  Callers leave those alone — the ISS-0065 lesson that absence must not
 *  render as a confident state.
 *
 *  A `busy` session is never cold whatever its timestamp says: the agent
 *  is mid-turn, so the cache is being read and re-written right now and
 *  the stale `ts` only means no state CHANGE has been published lately.
 */
function cacheTemperature(
  input: TemperatureInput | null | undefined,
  now: number,
  ttlMs: number = CACHE_TTL_MS,
): 'warm' | 'cold' | 'unknown' {
  if (!input || !input.ts) return 'unknown';
  if (input.state === 'busy') return 'warm';
  const started = Date.parse(input.ts);
  if (!Number.isFinite(started)) return 'unknown';
  // A timestamp in the future is a clock disagreement, not an old
  // session — treat it as warm rather than letting a skewed clock grey
  // out a live workspace.
  if (started > now) return 'warm';
  return now - started >= ttlMs ? 'cold' : 'warm';
}

// ---- the decisions the DOM merely applies (ISS-0110) ------------------
//
// `cacheTemperature` guarded the DECISION; the fix was three call sites
// and a renderer, and all four could be deleted with a green suite. So
// each one's judgment moves here, where the node suite can reach it, and
// the call site becomes a one-line adapter. Same route `healthMarks`
// took, and the reason that guard survived a review that went looking.

/** The `state-*` class a rail square should carry.
 *
 *  Cold demotes to `idle` — the branch `decayed_from` already took
 *  (ISS-0105). No new class, no new colour, no third animation.
 */
function railKey(
  state: { ts?: string | null; state?: string | null; decayed_from?: unknown } | null | undefined,
  now: number,
  ttlMs: number = CACHE_TTL_MS,
): string | null {
  if (!state || !state.state) return null;
  if (state.decayed_from) return 'idle';
  return cacheTemperature(state, now, ttlMs) === 'cold' ? 'idle' : state.state;
}

/** Which workspaces the NEEDS YOU panel should list.
 *
 *  Blocked on you AND still cheap to pick up. A cold entry leaves —
 *  its obligation lives on the grey square instead (TASK-0347).
 */
function attentionIds(
  states: Iterable<[string, { ts?: string | null; state?: string | null; decayed_from?: unknown }]>,
  now: number,
  ttlMs: number = CACHE_TTL_MS,
): string[] {
  const out: string[] = [];
  for (const [id, st] of states) {
    if (!st || st.decayed_from) continue;
    if (st.state !== 'needs-input' && st.state !== 'waiting') continue;
    if (cacheTemperature(st, now, ttlMs) === 'cold') continue;
    out.push(id);
  }
  return out;
}

interface BadgeInput {
  prefix_tokens: number;
  state: 'warm' | 'cooling' | 'cold';
  resume_cost_usd: number;
  warm_cost_usd: number;
  ttl_seconds: number;
  age_seconds: number;
  cooling_minutes_left?: number;
  model_switch?: {
    from: string; to: string; discarded_tokens: number; cost_usd: number;
  };
}

/** Weight, label, tooltip and tone for the strip's cache badge.
 *
 *  `tone` is the temperature, never overridden — a switch gets its own
 *  `switch` flag rather than borrowing cold's colour (ISS-0107).
 */
function cacheBadge(cache: BadgeInput | null | undefined): {
  weight: string; label: string; title: string; tone: string; switch: boolean;
} | null {
  if (!cache || !cache.prefix_tokens) return null;
  const tok = (n: number): string => {
    if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(n < 10_000_000 ? 1 : 0)}M`;
    if (n >= 1_000) return `${Math.round(n / 1_000)}k`;
    return String(n);
  };
  // Estimates: exact token counts, dollars from a drifting price table.
  const usd = (n: number): string => `~$${n.toFixed(2)}`;
  const mins = Math.round(cache.ttl_seconds / 60);
  const warm = usd(cache.warm_cost_usd);
  const cold = usd(cache.resume_cost_usd);
  const weight = tok(cache.prefix_tokens);

  let label: string;
  let title: string;
  if (cache.state === 'cold') {
    label = `cold · ${cold}`;
    title = `Cache older than its ${mins}min TTL. Next turn re-writes ${weight} tokens `
      + `(${cold}) instead of reading them (${warm}). Starting a fresh session costs neither.`;
  } else if (cache.state === 'cooling') {
    const left = cache.cooling_minutes_left ?? 0;
    label = `cooling ${left}m`;
    title = `About ${left} min before this session's cache passes its TTL. After that the `
      + `next turn re-writes ${weight} tokens (${cold}) instead of reading them (${warm}).`;
  } else {
    label = 'warm';
    title = `Last turn ${Math.round(cache.age_seconds / 60)} min ago, inside the ${mins}min `
      + `TTL. Next turn reads ${weight} tokens (${warm}) rather than re-writing them (${cold}).`;
  }
  if (cache.model_switch) {
    const sw = cache.model_switch;
    label = `model switch · ${usd(sw.cost_usd)}`;
    title = `Switching ${sw.from} → ${sw.to} discarded ${tok(sw.discarded_tokens)} cached `
      + `tokens; the cache is model-scoped, so that prefix was re-written at the cache-write `
      + `rate (${usd(sw.cost_usd)}). The cache is ${cache.state} now.`;
  }
  return { weight, label, title, tone: cache.state, switch: !!cache.model_switch };
}
