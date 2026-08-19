#!/usr/bin/env python3
"""Backfill one ledger per repo from today's scalar `mark:` ([[TASK-0529]]).

**It measures the gate delta and refuses to write until that number has been
printed.** That is not ceremony. This migration makes one repo's gate
substantially tighter — every one of `../your-trainer`'s 513 passes was earned
on Android and stops counting toward an iOS release the moment it lands in an
Android ledger — and *"quieter is the one direction a gate must never move
without somebody deciding it"* ([[ISS-0208]]) cuts both ways. The last three
schema changes to this corpus did not state their delta first.

**The dates are honest and imprecise, because there is nothing better.**
`verdict_date:` is non-empty on **0 of 671** acceptance notes fleet-wide, so
546 `pass` verdicts have no date at all. Entries carry the migration date with
`method: migration`, and a reason naming the pre-migration address out of
`migrated_from:`. Recovering true dates from `git log -L` over the pre-migration
document is possible and deliberately not done: it is partial, and precision
that looks total is worse than a stamp that says what it is.

Usage:
    backfill-ledger.py --repo-root . --platform android [--apply]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from project_os_cockpit import acceptance as A          # noqa: E402
from project_os_cockpit import ledger as L              # noqa: E402

#: The old scalar vocabulary to the event vocabulary ([[ADR-0037]] decision 6).
#:
#: **`canceled` maps to `na`, never to `excused`**, and the rule is written
#: down because decision 6 gave one old value two successors. A migration that
#: guessed would either make a permanent exception expire or make a per-release
#: one permanent. `na` is right for a backfill: nothing in the old field said
#: which release it belonged to, and `excused` is precisely the value that
#: claims one.
MARKS = {
    "done": "pass",
    "incomplete": "partial",
    "canceled": "na",
    #: `todo` becomes **no entry** ([[ADR-0037]] decision 5). You do not record
    #: that you did not do something.
    "todo": None,
    "": None,
    " ": None,
}
#: Refused rather than mapped. Measured 2026-08-19: each is written **0 times**
#: in all three repos, so a repo holding one is a repo this script has not been
#: read against — and `important`/`question` block while `rerun` is an
#: invalidation rather than a verdict. Guessing any of them would put a wrong
#: answer into a release gate.
REFUSED = {"important", "question", "rerun"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--platform", required=True,
                    help="the platform these verdicts were EARNED on")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    root = Path(args.repo_root).resolve()
    docs = root / "docs"
    #: **Indexed, because that is the corpus the GATE reads.**
    #:
    #: `A.load(docs)` with no index walks `docs/tests/acceptance/` only.
    #: Every production gate — `publication.release_payload`,
    #: `cockpit.gate_payload` — passes an index, and the indexed branch
    #: collects every `[[test]]` at `level: acceptance` ANYWHERE under
    #: `docs/`. In `../your-trainer` that is 581 checks / 62 blocking against
    #: the un-indexed 579 / 60.
    #:
    #: A migration that measures a smaller corpus than the gate it protects
    #: prints `+0` while destroying a recorded pass: a `mark: done` note
    #: outside `docs/tests/acceptance/` gets no ledger entry, `apply_ledger`
    #: then reads it as `todo`, and the gate moves by a number nobody saw.
    #: Found by independent review 2026-08-19; the two notes it would have hit
    #: today (`TST-0015`, `TST-0018`) are both `todo`, so the corpus was saved
    #: by luck rather than by the check.
    from project_os_cockpit.index import Index                # noqa: PLC0415
    suite = A.load(docs, Index.build(docs))
    if not suite.exists:
        print(f"backfill: no acceptance suite under {docs} — nothing to do")
        return 2
    if L.load(docs, args.platform):
        print(f"backfill: {args.platform} already has a ledger — refusing to "
              f"run twice")
        return 2

    before_blocking = len(suite.blocking())
    rows, skipped, refused = [], [], []
    for item in suite.items:
        if not item.note_id:
            skipped.append(f"{item.name}: no note id")
            continue
        mark = (item.mark or "").strip()
        if mark in REFUSED:
            refused.append(f"{item.note_id}: mark {mark!r}")
            continue
        if mark not in MARKS:
            refused.append(f"{item.note_id}: unrecognised mark {mark!r}")
            continue
        target = MARKS[mark]
        if target is None:
            continue
        rows.append((item, target))

    if refused:
        print(f"backfill: REFUSING — {len(refused)} mark(s) this script has "
              f"no rule for; nothing written:")
        for line in refused[:40]:
            print(f"  - {line}")
        return 1

    when = L._today()
    ledger = L.Ledger(platform=args.platform,
                      path=L.working_path(docs, args.platform))
    for item, mark in rows:
        source = item.migrated_from or "the pre-migration suite"
        reason = (f"Backfilled from `mark: {item.mark}`. The verdict predates "
                  f"the ledger and carries no date of its own; earned on "
                  f"{args.platform}. Original address: {source}.")
        ledger.entries.append(L.check_entry({
            "check": item.note_id, "mark": mark, "date": when,
            "by": "migration", "method": "migration", "reason": reason,
        }, where="backfill"))

    # ---- the delta, printed BEFORE anything is written -------------------
    # Resolved against the in-memory ledger rather than from disk, so the
    # number reported is the number that would land — a dry run that measures
    # something other than what it would write is worse than not measuring.
    resolved = L.resolve([ledger])
    after_blocking = sum(
        1 for i in suite.items
        if A.section_of(i) in A.MANUAL_SECTIONS
        and not ((v := resolved.get(i.note_id)) and v.clears)
    )
    print(f"backfill: {root.name} / {args.platform}")
    print(f"  checks            {len(suite.items)}")
    print(f"  entries written   {len(rows)}  "
          f"(no entry for {len(suite.items) - len(rows) - len(skipped)} "
          f"`todo` — absence is the initial state)")
    #: **A second platform's gate, which is the number that matters.**
    #:
    #: On the platform the verdicts were EARNED on, the delta is zero — that is
    #: the check that the backfill is lossless, and it is the boring half. The
    #: honesty gain is the other one: every Tier 1/2 check is owed on any
    #: platform with no ledger, because absence is the initial state
    #: ([[REQ-0054]]). That is not a gate that MOVED; it is a question the
    #: schema could not previously ask, answered for the first time.
    gating = sum(1 for i in suite.items if A.section_of(i) in A.MANUAL_SECTIONS)
    print(f"  GATE DELTA        {before_blocking} blocking -> "
          f"{after_blocking} blocking on {args.platform}"
          f"   ({after_blocking - before_blocking:+d})")
    print(f"  ON ANY OTHER PLATFORM  {gating} blocking — every Tier 1/2 check "
          f"is owed where nothing has been walked")
    if skipped:
        print(f"  skipped           {len(skipped)}")
        for line in skipped[:20]:
            print(f"    - {line}")

    if not args.apply:
        print("backfill: dry run — nothing written. Re-run with --apply.")
        return 0
    L.write(ledger)
    print(f"backfill: wrote {ledger.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
