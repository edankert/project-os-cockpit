---
type: "[[task]]"
id: TASK-0484
aliases: ["TASK-0484"]
title: "A writer for `status: retired`, which makes the Tier 2 → Tier 3 → remove path performable"
status: done
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

## Not done

`status: retired` is now **legal** for a test ([[TASK-0473-Test-Statuses-Gain-Active-And-Retired]]), which is the half that closes [[ISS-0178-A-Test-Cannot-Be-Retired]]'s vocabulary gap. No writer performs the transition yet, so TESTING.md's Tier 2 → Tier 3 → remove path is still described rather than performable.

## Done 2026-08-18

`note_writes.retire_check`, carrying both halves of TESTING.md's removal path — **promote** (Tier 2 → 3) and **retire** (`status: retired`).

Both are refused without a reason, and promotion is additionally refused without coverage: Tier 3 is where a check goes when a machine took it over, so promoting one that nothing covers is moving it out of the gating tiers on no evidence at all — the escape hatch rather than the lifecycle.

**Neither touches the mark or its date.** A retired check's verdict is the record of what was true when it was last walked, and clearing it would turn a deprecation into an erasure — which matters precisely when the automated test that replaced it is later deleted as redundant, because that is the moment the deletion looks safe.

`tier:` is written unquoted; it is an int in the schema, and `tier: "3"` would make every reader coerce a value the migration wrote as a number.
