---
type: "[[task]]"
id: TASK-0591
aliases: ["TASK-0591"]
title: "A retired check leaves the walk and the gate, and keeps its record in the note"
status: done
phase: "[[PHASE-041-The-Gate-Runs-Where-The-Checks-Are]]"
owner: user:edwin
created: 2026-08-30
updated: "2026-08-30"
reviewed_by: model:claude-opus-5
review_date: 2026-08-30
review_verdict: changes-requested
source: ["[[ISS-0265-A-Retired-Check-Still-Gates-The-Release]]"]
parent: "FEAT-0143"
effort: ""
due: ""
depends: ["TASK-0590"]
blocks: []
related: ["[[ISS-0249-The-Lever-That-Had-No-Handle]]"]
tests: []
---

# Retiring removes the obligation

## What changed

`_is_retired` and one filter in `acceptance.load`, applied after `apply_ledger` and before the `Suite` is built, on both note-shaped branches.

Placed there rather than in `blocking()`, the tier grouping and the facet builder, because all three read `Suite.items`: three filters is how two of them come to disagree, which is `REQ-0059`'s subject and has been found twice already in this phase.

## Measured on the repo that reported it

`../your-trainer`, `TST-0075` retired with a reason:

| | before | after |
|---|---|---|
| in the walkable suite | yes | no |
| in the `unclear` mark filter | yes | no |
| blocking the release | **yes** | no |
| gate total | 103 | **100** |

The note is untouched: `status: retired`, `mark: question`, `verdict_date: 2026-08-30`, and the reason appended under a `## Retired` heading. The record survives; the obligation does not.

## Guards

`test_a_retired_check_does_not_block_the_release` fails with the filter removed — run, not assumed.

`test_an_active_check_with_the_same_verdict_still_blocks` is the one that makes it mean something: the same note at `status: active`, same `mark: question`, must still block. Without it the first test passes for a filter keyed on the verdict, which would silently drop every unclear check in the fleet.

## Independent review, 2026-08-30 — changes-requested

The guards here are the best in the set — the second test is what makes the first mean something, and both were confirmed by mutation on both branches of `load`. Findings: [[ISS-0270]] — the *before* column of the measurement table is wrong (101, not 103) and contradicts the `104` stated three times elsewhere, and a one-check retire cannot move the gate by three; [[ISS-0269]] — the single-filter argument is right inside the package and stops at its edge, where `validate-docs.py` still counts the retired check as coverage.

Reviewed from a clean context (the notes and the diff, no authoring transcript) by `model:claude-opus-5`, the same model family as the author and a different session. Mutants were applied one at a time in a worktree at `c861414` and the full suite re-run; corpus figures were recomputed against `git archive fb99a751`, the `../your-trainer` state as of these commits.
