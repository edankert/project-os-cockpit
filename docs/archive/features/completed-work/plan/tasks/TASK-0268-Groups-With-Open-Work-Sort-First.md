---
type: "[[task]]"
id: TASK-0268
aliases: ["TASK-0268"]
title: "Groups that still contain open work sort above groups that do not, so the active phase is not buried under twenty finished ones"
status: done
phase: "[[PHASE-022-Completed-Work-Gets-Quieter]]"
owner: user:edwin
created: 2026-08-02
updated: 2026-08-02
source: ["[[FEAT-0056-Completed-Work-Ordering]]"]
parent: "[[FEAT-0056-Completed-Work-Ordering]]"
effort: S
depends: ["[[TASK-0267-One-Comparator-Open-Before-Done]]"]
blocks: []
related: ["[[ISS-0082-Phantom-Phase-Group-From-The-016-Merge]]"]
tests: ["[[TST-0023-Completed-Work-Ordering]]"]
---

# Groups with open work sort first

## Definition of Done

- **Phase groups** sort on `(band, phase order)` where band is *in flight / upcoming / finished*, read from the phase note's authored status — so an `active` phase precedes `planned` precedes `done`, and phase order is untouched within each band.
- **Severity buckets** sort on `(has no open work, severity rank)` — there is no authored status on a bucket, so the items are all there is to read.
- Applies to the features navigator (phase groups) and the issues navigator (severity buckets).
- The **tasks** navigator is exempt: its groups *are* statuses, so "groups with open work first" is already what its ordering means.

## Notes

Measured before building: **1 of 18** feature groups contains open work, and **0 of the 4** issue severity buckets do. Sorting alone therefore fixes the features view outright, and does nothing visible for issues until an issue is opened — which is the correct behaviour, not a shortfall.

**Revised at review.** A plain settled/unsettled split was wrong: `PHASE-999 · Future / Unphased` is permanently `planned`, so it outranked the phase in flight forever — and closing a phase settles it, so the phase just finished sank while the pen rose. The sort now bands on the phase note's **authored status**: in flight, upcoming, finished.

## Verification

The features navigator lists the phase containing open work first, regardless of its `order`. Guard fixes a corpus where the open phase has the highest `order` — the case where the two keys disagree.
