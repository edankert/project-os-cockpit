---
type: "[[task]]"
id: TASK-0586
aliases: ["TASK-0586"]
title: "`your-trainer` scopes REL-0013's acceptance checks from its own note — replacing the hand-written 32-of-623 markdown table with something derived"
status: done
phase: "[[PHASE-041-The-Gate-Runs-Where-The-Checks-Are]]"
owner: user:edwin
created: 2026-08-29
updated: 2026-08-29
source: ["[[ISS-0209-The-Acceptance-Gate-Reaches-No-Fleet-Repo]]"]
parent: "FEAT-0143"
effort: ""
due: ""
depends: ["TASK-0584"]
blocks: []
related: ["[[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]]", "[[FEAT-0142-A-Release-Says-What-Is-In-It]]"]
tests: []
---

# `your-trainer` scopes its own release

## Definition of Done
- [x] `REL-0013` carries `features:` (and `held_back:` with reasons where a feature is excluded), so its acceptance scope is derived from the note.
- [x] The hand-written 32-of-623 markdown table is replaced by, or reconciled against, the derived selection.
- [x] Any gap between what [[FEAT-0142-A-Release-Says-What-Is-In-It]] built and what `your-trainer` can consume is **filed**, not narrated.

## Notes

This is [[PHASE-041]]'s sixth exit criterion and the one that turns a tooling migration into the thing [[ADR-0040]] decided. On 2026-08-29 `your-trainer` was asked to do exactly this and could not: the scoping was done by hand from `git diff v2.1.6..HEAD`, mapping 14 changed Kotlin files onto `area:` groupings by judgement.

**Assessed after [[TASK-0584]] lands**, because what is missing cannot be known until the repo is running the rules. If the gap turns out to be cockpit-side rather than validator-side, that is a finding for this task to record, not a reason to widen it.
