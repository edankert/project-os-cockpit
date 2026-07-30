// The contribution grid's pure logic (FEAT-0053 / TASK-0259).
//
// Split out for the reason the PHASE-013 review made unarguable: a
// decision inside a DOM function can only be guarded by grepping the
// built bundle, and that guard survives the mutation that breaks it.
// Cell state, week layout and year detection are all pure — dates and
// counts in, a grid description out.
//
// Declares no imports and no exports: `renderer.ts` is loaded as a plain
// <script>, so this is loaded the same way and these become globals.

interface GridDay {
  transitions: number;
  commits: number;
}

/** A cell's state. `absent` is NOT `empty` — a day before the first
 *  commit is a day the project did not exist, and rendering the two
 *  identically is why every young repo's contribution graph reads as
 *  neglect. This corpus would show 40 of 52 weeks as apparent
 *  inactivity. */
type CellState = 'absent' | 'empty' | 1 | 2 | 3 | 4;

interface GridCell {
  date: string;          // YYYY-MM-DD
  state: CellState;
  transitions: number;
  commits: number;
}

/** `YYYY-MM-DD` for a Date, in local time — `toISOString` would shift
 *  the date across the boundary for anyone east or west of UTC, which
 *  is a whole day wrong for the cell you clicked. */
function gridDateKey(d: Date): string {
  const m = `${d.getMonth() + 1}`.padStart(2, '0');
  const day = `${d.getDate()}`.padStart(2, '0');
  return `${d.getFullYear()}-${m}-${day}`;
}

/** Which intensity step a count falls in, given the payload's cuts.
 *
 *  The cuts are quartiles of this repo's own ACTIVE days. GitHub's fixed
 *  1/4/7/10 saturates here — measured, the median active day carries 34
 *  transitions — so every lit cell would land in the top step and the
 *  grid would carry one bit per day: worked, or did not.
 */
function gridStep(count: number, buckets: number[]): CellState {
  if (count <= 0) return 'empty';
  if (buckets.length < 3) return 4;
  if (count <= buckets[0]) return 1;
  if (count <= buckets[1]) return 2;
  if (count <= buckets[2]) return 3;
  return 4;
}

/** The grid as columns of weeks, oldest first, ending today.
 *
 *  Columns start on Sunday to match the shape people already know. The
 *  leading partial week is padded with `absent` cells rather than
 *  omitted, so the weekday rows stay aligned.
 */
function buildGridWeeks(
  days: Record<string, GridDay>,
  firstCommit: string | null,
  buckets: number[],
  today: Date,
  weeks = 52,
): GridCell[][] {
  const end = new Date(today.getFullYear(), today.getMonth(), today.getDate());
  // Walk back to the Sunday that starts the window.
  const start = new Date(end);
  start.setDate(start.getDate() - (weeks * 7 - 1));
  start.setDate(start.getDate() - start.getDay());

  const out: GridCell[][] = [];
  const cursor = new Date(start);
  while (cursor <= end) {
    const column: GridCell[] = [];
    for (let i = 0; i < 7; i++) {
      const key = gridDateKey(cursor);
      const entry = days[key];
      let state: CellState;
      if (cursor > end) {
        state = 'absent';                       // the rest of this week
      } else if (firstCommit && key < firstCommit) {
        state = 'absent';                       // the project did not exist
      } else {
        state = gridStep(entry?.transitions ?? 0, buckets);
      }
      column.push({
        date: key,
        state,
        transitions: entry?.transitions ?? 0,
        commits: entry?.commits ?? 0,
      });
      cursor.setDate(cursor.getDate() + 1);
    }
    out.push(column);
  }
  return out;
}

/** Distinct calendar years covered by the history.
 *
 *  Year controls render only when this returns more than one: a
 *  selector on a twelve-week repo offers navigation to nothing. Same
 *  rule the fleet roll-up uses for its empty state.
 */
function gridYears(firstCommit: string | null, lastCommit: string | null): number[] {
  if (!firstCommit || !lastCommit) return [];
  const from = Number(firstCommit.slice(0, 4));
  const to = Number(lastCommit.slice(0, 4));
  if (!Number.isFinite(from) || !Number.isFinite(to) || to < from) return [];
  const years: number[] = [];
  for (let y = to; y >= from; y--) years.push(y);
  return years;
}

/** Month labels: the column index where each month first appears. */
function gridMonthLabels(weeks: GridCell[][]): Array<{ col: number; label: string }> {
  const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const out: Array<{ col: number; label: string }> = [];
  let last = '';
  weeks.forEach((column, col) => {
    const month = column[0].date.slice(0, 7);
    if (month !== last) {
      last = month;
      out.push({ col, label: MONTHS[Number(month.slice(5, 7)) - 1] });
    }
  });
  return out;
}
