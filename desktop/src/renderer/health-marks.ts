// The fleet-health square encoding, as a pure function (FEAT-0028 / ISS-0074).
//
// Split out of `applyHealthToSquare` so the decision can be tested without a
// DOM. The independent review of PHASE-013 demonstrated why: the guard that
// claimed to protect "unknown paints nothing" compared string indices in the
// built bundle, and a mutation that ADDED `health-ok` for `unknown` — the
// exact ISS-0065 failure the rule exists to prevent — kept the literal in
// place and passed every test.
//
// This file deliberately declares no imports and no exports: `renderer.ts`
// is loaded as a plain `<script>`, not a module (see the note at the top of
// it), so this is loaded the same way and `healthMarks` becomes a global.
// The node suite reads the built file and evaluates it, which is why the
// shape matters.

interface HealthMarkRow {
  state: 'ok' | 'failing' | 'unavailable' | 'unknown';
  errors: number;
  stale?: boolean;
}

interface HealthMarks {
  /** Classes to add to the square. Empty means: paint nothing. */
  classes: string[];
  /** Badge text, or null for no badge. */
  badge: string | null;
}

/** What a square should carry for a given validator state.
 *
 *  `unknown` — and a missing row — yield NO classes and NO badge. Not a
 *  reassuring grey, not a neutral ring: nothing. A fleet dashboard whose
 *  default state is indistinguishable from "passed" teaches people to read
 *  absence as health, which is the defect ISS-0065 recorded.
 */
function healthMarks(row: HealthMarkRow | null | undefined): HealthMarks {
  if (!row || row.state === 'unknown') return { classes: [], badge: null };
  const classes = [`health-${row.state}`];
  if (row.stale) classes.push('health-stale');
  // Only `failing` carries a numeral, and only when there is a number to
  // carry — a badge reading `0` would be a drift report with no drift.
  const badge = row.state === 'failing' && row.errors > 0
    ? (row.errors > 99 ? '99+' : String(row.errors))
    : null;
  return { classes, badge };
}
