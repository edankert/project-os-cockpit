---
type: "[[issue]]"
id: ISS-0112
aliases: ["ISS-0112"]
title: "FEAT-0081 does not link half its own tasks or the issue it is credited with fixing, while the change note claims the feature was updated — the note and SNAPSHOT.yaml disagree and the validator passes"
status: fixed
phase: ""
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
source: ["review:independent-2026-08-06"]
severity: medium
component: "docs"
related: ["[[FEAT-0081-What-A-Session-Costs-To-Keep-Alive]]", "[[ISS-0105-The-Rail-Pulses-The-Same-For-Two-Minutes-And-Two-Hundred-Hours]]", "[[CHG-20260806-Cold-Sessions-Read-Grey]]"]
tests: []
---

# FEAT-0081 was never updated for its second surface

## Problem

`CHG-20260806-Cold-Sessions-Read-Grey` records under Documentation Coverage:

> features: updated — [[FEAT-0081-What-A-Session-Costs-To-Keep-Alive]] reopened for its second surface, then closed

The feature note is not in that commit. `git show --name-only 165276b` stages eleven files; `docs/features/session-economics/FEAT-0081-*.md` and `plan/PLAN.md` are not among them, and `git log` shows FEAT-0081 last touched by the *first* commit. The claim is false as written.

The consequences are visible in the frontmatter, where the note and the snapshot now disagree:

| | FEAT-0081 note | SNAPSHOT.yaml |
|---|---|---|
| `tasks` | TASK-0343, 0344, 0345 | TASK-0343 … **TASK-0347** |
| `fixes` | ISS-0104 | ISS-0104, **ISS-0105** |
| `related` | no ISS-0105 | — |

So the feature that `SNAPSHOT.yaml` says fixes ISS-0105 and owns TASK-0346/0347 does not mention any of them, and its body says nothing about the rail or the NEEDS YOU list:

- **Scope** lists four in-scope items, none about the rail; the change note describes rail and panel behaviour as this feature's second surface.
- **Acceptance** has six criteria, none covering "a cold session reads grey" or "a cold session leaves NEEDS YOU" — the two user-visible behaviours the feature was closed on.
- **Links → Tasks** lists three of five.

The feature is `status: done` with the acceptance criteria for half its delivered behaviour absent. Under `sync-snapshot.py`'s contract the note is the authored source of state (ADR-0009), so where they differ, the *note* is the record — and it is the less complete of the two.

## Why the validator did not catch it

`validate-docs.sh` returns OK. Membership (`tasks:`, `fixes:`) is curation the sync script deliberately leaves alone, and nothing checks the reverse direction: a task's `parent:` pointing at a feature that does not list it back. `--report-unregistered` covers notes the snapshot cannot see, not links the note is missing.

That is the more useful half of this finding: **the reverse-link check does not exist**, so this class of drift is invisible to every gate in the repo.

## Expected

- FEAT-0081's `tasks:`, `fixes:`, `related:`, Scope, Acceptance and Links updated to cover TASK-0346, TASK-0347 and ISS-0105.
- The change note's coverage line corrected, or the feature actually updated so it becomes true.
- A validator check that a `parent:`/`fixes:` relationship is declared on both ends.

## Actual

A feature closed as done whose note omits the second of its two surfaces, and a change note that says otherwise.

## Notes

Filed as a documentation defect rather than a process complaint. The two commits are unusually well documented — the CHG notes disclose their own gaps, and the anti-feature reasoning in FEAT-0081 is the sort of thing that is normally lost. That is exactly why the one unchecked claim matters: everything else in these notes has earned the reader's trust.

## Next Actions

- [x] Update FEAT-0081 (frontmatter + Scope + Acceptance + Links)
- [x] Correct the coverage line in [[CHG-20260806-Cold-Sessions-Read-Grey]]
- [x] Add a reverse-link check to `validate-docs.sh`: every note with `parent: FEAT-X` appears in FEAT-X's `tasks:`; every `fixes:` has a matching `parent:`/`related:`
