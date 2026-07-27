---
type: "[[task]]"
id: TASK-0218
aliases: ["TASK-0218"]
title: "Design review through the existing desk, per-region verdicts"
status: done
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-27
updated: 2026-07-27
source: ["user request 2026-07-27"]
parent: "[[FEAT-0042-Design-Bench]]"
effort: "S"
depends: ["[[TASK-0217]]"]
blocks: []
related: ["[[FEAT-0041-Review-Desk]]"]
tests: []
---

# Design review in the desk

## Definition of Done

- [x] A design awaiting review appears in the `~review` queue alongside proposals, questions and manual tests — evidence: `QUEUE_INTAKE_STATES["design"] = ("proposed",)` — `draft` and `implemented` deliberately absent
- [x] Review offers per-region verdicts plus an overall outcome, reusing the proposal-set shape (per-item ticks + Accept / Request changes / Reject) — evidence: comments are per-region ([[TASK-0217]]); the overall verdict is `stamp_design_verdict`
- [x] The verdict is written through `note_writes.py` into the design note's existing review fields — no new status vocabulary — evidence: `DESIGN_REVIEW_FIELDS`; the allow-list test was updated deliberately with its reason
- [x] The verdict is **never auto-stamped**: the machine gathers, the human decides — evidence: `accept` comes from the caller; the endpoint records, never decides
- [x] Requesting changes leaves the design in the queue with the per-region comments attached — evidence: `accept: null` writes the verdict without a status transition, so it stays `proposed`
- [x] Accepting records what was accepted — which revision, which regions, on what date — evidence: `design_revision` is required and validated against real history; `test_a_verdict_naming_a_revision_that_does_not_exist_is_refused`

## Steps

- [x] Add designs to the queue intake states
- [x] Reuse `buildSingleNoteReview`'s shape for per-region verdicts
- [x] Extend the guarded writer's allow-list; no new fields beyond the review triple and the revision reference
- [x] Test the accept and request-changes paths against a real design note

## Result

**`design_revision` is the field that makes this honest.** A verdict given to v3 says nothing about v6, so the endpoint requires the revision *and validates it against the artifact's real git history*. Without that validation the pin would be decoration — a verdict could name anything and the laundering it exists to prevent would be back.

Two vocabulary decisions, both reusing existing values:

- **Accepting does not mark a design `implemented`.** That is what the code shipping means, and only [[TASK-0219]]'s parity check can honestly claim it. Accepted means accepted.
- **Rejection is `cancelled`, not `superseded`.** Superseded means a *later design replaced it* — a different fact about the future than "this one was turned down".

Requesting changes writes the verdict with no status transition, so the design stays `proposed` and stays in the queue.

## Notes

Almost entirely reuse. FEAT-0041 already built the queue, the proposal-set review shape, the guarded write-back and 37 tests around it. A design review is the same interaction with regions in place of items.

"Accepting records which revision" matters more than it sounds: a verdict against v3 says nothing about v6, and a design surface that loses that distinction would let an old approval launder a new design. The revision reference is what stops that.
