---
type: "[[change]]"
id: CHG-20260730-Phase-Hygiene
aliases: ["CHG-20260730-Phase-Hygiene"]
title: "Sixteen delivered notes re-homed out of the parking-lot phase, each from evidence already in the note"
status: merged
phase: "[[PHASE-015-Phase-Hygiene]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["[[ISS-0074-Sixteen-Delivered-Notes-Stranded-In-The-Parking-Lot]]"]
related: ["[[PHASE-014-Project-Inbox]]", "[[PHASE-999-Future]]", "[[ISS-0074-Sixteen-Delivered-Notes-Stranded-In-The-Parking-Lot]]"]
tests: []
---

# Phase hygiene

No code changed. This is a record correction: sixteen notes claimed a phase that says the work has not been planned yet, while being finished.

## The attributions, and what justifies each

**Fifteen resolve from a link already in the note.** No judgement was exercised on these — the target is whatever the parent, the fix, or the implemented feature already names.

| Notes | To | Evidence |
|---|---|---|
| TASK-0111, TASK-0112, TASK-0113 | PHASE-011 | `parent: [[FEAT-0018]]`, which is `done` in PHASE-011 |
| TST-0016 | PHASE-011 | lives at `features/verification-health/plan/tests/` — FEAT-0018's own tree |
| TASK-0213 | PHASE-007 | `parent: [[FEAT-0025]]` |
| ISS-0032 | PHASE-007 | `fixed_by: [[TASK-0213]]` |
| REQ-0019 | PHASE-007 | `implements: [[FEAT-0032]]` |
| REQ-0020 | PHASE-007 | `implements: [[FEAT-0034]]` |
| TASK-0230 | PHASE-013 | `parent: [[FEAT-0044]]`, closed there yesterday beside TASK-0231 |
| ISS-0059 | PHASE-013 | `related:` FEAT-0044 / TASK-0230 / TASK-0231; unblocked by that rollout |
| TASK-0232, TASK-0233, TASK-0234 | PHASE-014 | `parent: [[FEAT-0045]]` |
| ISS-0060, ISS-0061 | PHASE-014 | `related:` FEAT-0045 and its tasks; both are inbox defects |

**The sixteenth needed a phase written for it.** [[FEAT-0045]] was built on 2026-07-28, in a day, on request, between two phases whose scope does not cover it — [[PHASE-009]] is design surfaces and [[PHASE-010]] is which page each *note type* belongs on, and an inbox is not a note type. Backdating it into either would have been the fabrication the rule exists to prevent, so [[PHASE-014]] was written as a record. Its note says so in its first section, and `order: 14` reflects when the note was allocated rather than when the work happened.

That is the escape hatch working as intended: not an exemption, a record. The alternative was a second sentinel meaning "delivered, but unphased", which is machinery for a case this corpus contains once.

**[[PHASE-011]] closed FEAT-0045; it did not deliver it.** Its close-out shares a change note with FEAT-0018's because both were gated on a check nobody had run — an opportunistic pairing, not shared scope. PHASE-011's `features:` list never named FEAT-0045, and following the change note rather than the scope would have put the feature in a phase that never planned it.

## What else changed

- **The sentinel note gained its missing exit.** [[PHASE-999]] documented only "when the item gets serious planning, re-phase it". The exit that happens most — the item gets built — is now written, with the reason it is a category error rather than a stale value.
- **Its membership list was stale.** It still named FEAT-0018 and FEAT-0028 after both went `done` and were re-phased. Hand-kept membership beside self-declaring members is the dual-write [[ADR-0009]] removed for statuses; flagged upstream rather than fixed by hand here.
- **`docs/PHASES.md`** gained PHASE-014 and the two-exit note on PHASE-999.
- **Two guards**, in this repo's suite rather than the template-owned validator ([[ISS-0026]]): `test_no_terminal_note_sits_in_the_parking_lot`, and `test_the_parking_lot_still_holds_the_work_it_is_for` — because emptying the sentinel would satisfy the first while destroying what it protects. Both mutation-verified.

## Two things this turned up

**An existing guard caught my own half-finished work.** `test_the_snapshot_phase_matches_the_note` failed after the notes moved, because `sync-snapshot.py` propagates status, counters and metrics but **not** `phase` — so the snapshot kept four stale values. Exactly what that guard is for, and worth recording that the dual-write ADR-0009 removed for statuses still exists for phases.

**The corpus uses two spellings.** Both `[[PHASE-999-Future]]` and the bare `[[PHASE-999]]` occur. My first correction pass matched only the long form and stopped partway through, leaving eleven notes moved and five not. The guard matches the resolved ID instead. `docs/PHASES.md` already records a near-miss of the same shape — `PHASE-999-Unscheduled`, a dangling link on 13 notes that never existed.

## Not done here

The **rule** is upstream: `LIFECYCLE.md`, `STATUSES.md` and `validate-docs.py` are template-owned and this repo holds the validator byte-identical. Filed as `project-os-dev` ISS-0027, proposing the mirror of `PHASE-CHILDREN` over the same `PHASE_RESOLVED` table, plus deriving a child's phase from its parent so the stranded-children class cannot recur at all.

The rest of the fleet keeps its backlog — `your-trainer` 72 notes, `project-os-dev` 42. Correcting those now would be sixteen judgements times three repos with no check to hold them, and [[PHASE-013]] already put other repos' corpora out of scope.
