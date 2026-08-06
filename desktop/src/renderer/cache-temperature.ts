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
