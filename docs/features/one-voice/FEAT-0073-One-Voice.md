---
type: "[[feature]]"
id: FEAT-0073
aliases: ["FEAT-0073"]
title: "One voice — empty states that say what would appear, the eye toggle retired or defended, the exceptions written down, and mode 1 decided once"
status: done
phase: "[[PHASE-026-The-Returning-Human]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["Review 2026-08-03, consistency findings; the mode-1 twin drifted three times in two days"]
goal: "Spend the consistency residue deliberately: one empty-state sentence pattern; the collapse-completed toggle retired or explicitly defended; the desk and Library exceptions recorded in DES-0002; and mode 1's fate taken as an ADR with the drift record as evidence."
requirements: []
tasks:
  - "[[TASK-0318-The-Empty-State-Sweep]]"
  - "[[TASK-0319-The-Toggle-Decided]]"
  - "[[TASK-0320-The-Exceptions-Recorded]]"
  - "[[TASK-0321-The-Mode-1-ADR]]"
release: "[[REL-0001-The-Human-Has-Levers]]"
related: ["[[DES-0002-Cockpit-Design-System]]"]
tests: []
---

# One voice

## Goal

Four small debts, each cheap alone and each a repeat offender when left: three empty-state voices; a toggle that duplicates the per-card defaults PHASE-022 built (two mechanisms for one idea is how the pill got wrong twice); two deliberate exceptions living only in issue notes where the next session cannot inherit them; and a hand-written mode-1 twin whose every UI change costs double — three drifts in two days, all caught by review, none by tests-as-first-written.

## Out of Scope

- Executing the mode-1 ADR's outcome. Authoring the decision with evidence is this feature; the retirement or investment it chooses is its own scoped work.

## Acceptance

- [x] Every empty state says what the pane shows and the shortest path to having some, in one voice — nine rewritten, guarded by a sweep over the literals in `renderer.ts` ([[TASK-0318]])
- [x] Two deliberate exceptions are recorded as data with their reasons, and a test asserts each still matches a live literal so the list cannot become permission for strings nobody renders
- [x] The collapse-completed eye is **defended in writing** rather than retired — it folds the completed tail of *mixed* groups, which per-card defaults cannot do ([[TASK-0319]], [[DES-0002]])
- [x] [[DES-0002]] carries a `Deliberate exceptions` section: obligations-not-collections, files-not-lifecycle-notes ([[TASK-0320]])
- [x] Mode 1 is decided once, with the drift record as evidence — [[ADR-0021]], `proposed` for the actuator row ([[TASK-0321]])

## Verification

`tests/test_empty_state_voice.py` — 4 tests, including a floor assertion so a sweep that swept nothing cannot pass.

The ADR arrived `proposed`, which is the point: authoring the decision with evidence was this feature's scope, and executing its outcome is [[PHASE-029]]'s, explicitly out of [[REL-0001]].
