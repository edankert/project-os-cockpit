---
type: "[[task]]"
id: TASK-0353
aliases: ["TASK-0353"]
title: "FEAT-0081 gains the surface it was closed on, and the validator learns to check a relationship from both ends"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
source: ["review:independent"]
parent: "[[FEAT-0081-What-A-Session-Costs-To-Keep-Alive]]"
effort: M
due: ""
depends: ["[[TASK-0351-Pure-Decisions-For-The-Rail-And-The-Badge]]"]
blocks: []
related: ["[[ISS-0112-FEAT-0081-Was-Never-Updated-For-Its-Second-Surface]]"]
tests: []
---

# The feature note catches up, and links are checked both ways

Fixes [[ISS-0112-FEAT-0081-Was-Never-Updated-For-Its-Second-Surface]].

## Definition of Done
- [x] FEAT-0081's `tasks:`, `fixes:`, `related:`, Scope, Acceptance and Links cover TASK-0346, TASK-0347 and ISS-0105 — the second surface it was closed on.
- [x] Acceptance gains criteria for the two user-visible behaviours that had none: a cold session reads grey, and a cold session leaves the NEEDS YOU list.
- [x] The false coverage line in [[CHG-20260806-Cold-Sessions-Read-Grey]] is corrected.
- [x] **The validator checks the reverse direction**: a note declaring `parent:` or `fixes:` must be declared back by the note it names. This is the generalisable half — the drift was invisible to every gate in the repo.
- [x] The new check is proven by a test that fails on the drift as it actually existed.

## Notes
Membership is curation `sync-snapshot.py` deliberately leaves alone, and nothing looked the other way down the link. The feature was `done` with acceptance criteria absent for half its delivered behaviour, and the snapshot and the note disagreed about what it even contained.
