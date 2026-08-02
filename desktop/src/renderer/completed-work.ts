// Ordering completed work rather than removing it (FEAT-0056).
//
// Every navigator groups on a different axis — the tasks pane on status,
// issues on severity, features on phase order, the right-hand context
// pane on note *type* — and STATE IS ORTHOGONAL TO ALL FOUR. No grouping
// axis can carry it. That is why a global Hide-completed switch got
// invented: it sidesteps the ordering problem rather than solving it.
//
// It sidestepped it badly. Measured 2026-08-02 — 99% of this repo's
// lifecycle notes are terminal (tasks 99%, features 98%, and issues,
// changes and requirements all at 100%; 90% across every note type) — with the switch on:
//
//   Features            1 of 18 phase groups survived, holding 1 row
//   Issues              0 of the 4 severity buckets survived; only the
//                       3 risk buckets remained, and risks are not issues
//   Tasks               5 item rows of 270, in 2 of 5 groups
//   Context pane        FEAT-0051 and ISS-0080 emptied ENTIRELY
//
// The rule this module encodes is FOLD ON VOLUME, NEVER ON MEANING. A
// completed task under its feature is what the feature is made of; a
// completed task in a list of 261 is something you scroll past. Same
// status, different job — so the response differs by pane, not by status.
//
// Split out for the reason the PHASE-013 review made unarguable: a
// decision inside a DOM function can only be guarded by grepping the
// built bundle, and that guard survives the mutation that breaks it.
//
// Declares no imports and no exports: `renderer.ts` is loaded as a plain
// <script>, so this is loaded the same way and these become globals.

interface StatefulItem {
  status?: string;
}

// The vocabulary is `statuses.py`'s COMPLETED_STATUSES — done band plus
// archived band. Restated here because the renderer cannot import Python,
// and checked against it by `tests/test_status_vocabulary.py`, which
// parses this file. ISS-0023 is what happens without that check: the
// vocabulary lived in eight places and drifted in three, so `implemented`
// was coloured done but ranked open and a corpus of 97 implemented
// requirements never cleared the navigator.
const COMPLETED_WORK_STATUSES: ReadonlySet<string> = new Set([
  'done', 'merged', 'fixed', 'resolved',
  'fulfilled', 'met', 'complete', 'implemented',
  'verified', 'passing', 'published', 'released', 'closed',
  'obsolete', 'retired', 'cancelled', 'superseded',
  'declined', 'reverted', 'deprecated',
]);

/** 1 for terminal work, 0 for anything else.
 *
 *  An UNRECOGNISED status ranks open, deliberately. Sinking it would
 *  quietly bury a note whose status is a typo — hiding exactly the thing
 *  worth noticing. */
function completionRank(item: StatefulItem | undefined): 0 | 1 {
  const s = item && item.status ? String(item.status).toLowerCase() : '';
  return COMPLETED_WORK_STATUSES.has(s) ? 1 : 0;
}

/** Open work first, existing order preserved beneath.
 *
 *  `Array.prototype.sort` is stable (spec-guaranteed since ES2019), so
 *  this moves terminal items to the back and changes nothing else: the
 *  order the server sent — ID, severity, path — survives as the tiebreak
 *  for free, and no row shifts for a reason the reader cannot see. */
function openFirst<T extends StatefulItem>(items: readonly T[] | null | undefined): T[] {
  // Tolerates null/undefined: the server omits empty link arrays, and a
  // sort that throws on a missing group would blank the whole pane.
  // Mode 1's twin has always tolerated it; the review found mode 3 did
  // not.
  if (!items) return [];
  return items.slice().sort((a, b) => completionRank(a) - completionRank(b));
}

/** True when every item is terminal — the group has nothing to act on.
 *
 *  An EMPTY group counts as settled for the same reason. */
function groupIsSettled(items: readonly StatefulItem[]): boolean {
  return !items.some((it) => completionRank(it) === 0);
}

/** How a group renders once it is longer than `limit`.
 *
 *  The condition is LENGTH, never status: an over-long group of entirely
 *  open items folds identically. Folding on status is what produced the
 *  empty views this feature exists to undo (TASK-0270).
 *
 *  `collapse` is the Hide-completed switch's new meaning: it folds at the
 *  first terminal item rather than removing anything. A fully settled
 *  group therefore cuts to an empty `head` — and stays visible through
 *  its header and its count, which is where visibility belongs.
 *
 *  `head.length + hidden` always equals `items.length`. The count is
 *  never optional and callers must always render it: a fold that hides
 *  the fact that it hid something is indistinguishable from having
 *  nothing there — exactly how the old switch emptied three views
 *  without ever looking broken. */
function foldGroup<T extends StatefulItem>(
  items: readonly T[] | null | undefined,
  limit: number,
  collapse: boolean,
): { head: T[]; hidden: number } {
  const ordered = openFirst(items);
  if (ordered.length === 0) return { head: [], hidden: 0 };

  // A negative or non-finite limit silently dropped a row and made
  // `hidden` over-report — `head + hidden` no longer summed to the input.
  // Unreachable through the constant, but the invariant is the whole
  // basis for trusting the count, so it holds for every input rather than
  // for the inputs we happen to pass.
  const cap = Number.isFinite(limit) ? Math.max(0, Math.floor(limit)) : ordered.length;

  let cut = ordered.length;
  if (collapse) {
    const firstDone = ordered.findIndex((it) => completionRank(it) === 1);
    // An entirely settled group cuts to ZERO rows, not one. Showing a
    // single arbitrary row — the first by ID — tells the reader nothing
    // the count does not, and reads as if that item were somehow the
    // notable one. `Done · … 257 more` is the honest rendering.
    //
    // The group does not disappear: its header always renders, and
    // `hidden` is always shown. Visibility comes from the header and the
    // count, never from a sample.
    if (firstDone >= 0) cut = firstDone;
  }
  if (cut > cap) cut = cap;
  return { head: ordered.slice(0, cut), hidden: ordered.length - cut };
}

/** The context pane's rows: ordered, folded on length, NEVER on state.
 *
 *  Deliberately takes no `collapse` parameter. The first version of this
 *  feature had the caller pass `false` and review reverted it to
 *  `hideCompleted` in one character with **every test still green** — the
 *  pane whose emptying was the whole reason for the phase had no guard on
 *  either surface.
 *
 *  Removing the parameter is what makes that mutation impossible to write
 *  by accident: filtering this pane by state now requires editing this
 *  function, and `test_the_context_pane_cannot_be_made_to_filter` fails
 *  when you do. A comment saying "do not pass true here" would not have.
 *
 *  The left pane keeps its `collapse` because there the switch is a real
 *  control; here it never was. */
function contextGroupRows<T extends StatefulItem>(
  items: readonly T[] | null | undefined,
  limit: number,
): { head: T[]; hidden: number } {
  return foldGroup(items, limit, false);
}

/** What a group's head should say about its items' status (TASK-0272).
 *
 *  `null` means "the statuses vary — leave the per-row chips alone",
 *  because there the chip is the only thing distinguishing one row from
 *  another. A single status means the head can say it once and every row
 *  can drop it.
 *
 *  The rule, stated generally: **repeat a fact per-row only when it
 *  varies per-row.** The tasks view prints the word "done" 261 times
 *  without it, which is the same instinct that made a status *filter*
 *  look reasonable — treating a near-constant as information.
 */
function uniformStatus(items: readonly StatefulItem[]): string | null {
  if (!items.length) return null;
  const first = (items[0].status || '').toLowerCase();
  if (!first) return null;
  for (const it of items) {
    if ((it.status || '').toLowerCase() !== first) return null;
  }
  return first;
}

/** The count-and-status suffix for a group head: `19 · done`, `6 · 5 done`,
 *  or just `4` when nothing useful can be said about the mix. */
function groupHeadSummary(items: readonly StatefulItem[]): string {
  const n = items.length;
  if (!n) return '';
  const uniform = uniformStatus(items);
  if (uniform) return `${n} · ${uniform}`;
  const done = items.filter((it) => completionRank(it) === 1).length;
  return done ? `${n} · ${done} done` : String(n);
}

/** The short handle for a note ID, for the ID column (ISS-0084).
 *
 *  Every note type but one carries a counter-allocated ID — `FEAT-0057`,
 *  `ISS-0084`. Changes carry `CHG-YYYYMMDD-Short-Description`
 *  (`LIFECYCLE.md` line 95), so their ID *is* a description, and a row
 *  rendering `id · title` printed the description twice — at three to
 *  five times the width of every other ID, in a column whose width is set
 *  by its widest member.
 *
 *  The date prefix is the handle; the title carries the description,
 *  which is the division of labour every other row already has. Two
 *  changes on one day share a handle, and that is honest: the date is the
 *  identity granularity this scheme chose.
 *
 *  Display only. `id:` stays canonical and links resolve on the full
 *  value — this must never be fed back into a lookup.
 */
function shortNoteId(id: string | undefined): string {
  if (!id) return '';
  const m = /^(CHG-\d{8})-.+/.exec(id);
  return m ? m[1] : id;
}
