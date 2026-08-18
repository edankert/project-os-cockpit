---
type: "[[task]]"
id: TASK-0484
aliases: ["TASK-0484"]
title: "A writer for `status: retired`, which makes the Tier 2 → Tier 3 → remove path performable"
status: backlog
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
source: ["[[FEAT-0120-The-Automation-Path]]"]
parent: "[[FEAT-0120-The-Automation-Path]]"
effort: S
depends: ["[[TASK-0473-Test-Statuses-Gain-Active-And-Retired]]"]
blocks: []
related: []
tests: []
---

# A writer for `retired`

TESTING.md describes a lifecycle nothing can perform: *"when unit tests are written that cover the same logic, the acceptance test can be moved from Tier 2 to Tier 3 … after the next verified release, remove the Tier 3 test."* No code writes `tier:`, and until [[TASK-0473-Test-Statuses-Gain-Active-And-Retired]] no code could write a terminal status either.

Two writes, both refused without a reason: **promote** (tier 2 → 3, requiring a `covered_by:` that resolves) and **retire** (`status: retired`, requiring the release that verified it).

**Retiring is not deleting** — LIFECYCLE.md forbids deleting completed notes, and a retired acceptance test is the record that the behaviour was once walked by hand and is now covered by a machine. That is exactly the history somebody will want when the automated test is later deleted as redundant.

Done when: both transitions are writable, both refuse without their justification, and a retired test leaves the gate without leaving the corpus.
