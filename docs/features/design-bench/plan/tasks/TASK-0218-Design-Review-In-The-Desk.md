---
type: "[[task]]"
id: TASK-0218
aliases: ["TASK-0218"]
title: "Design review through the existing desk, per-region verdicts"
status: backlog
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

- [ ] A design awaiting review appears in the `~review` queue alongside proposals, questions and manual tests
- [ ] Review offers per-region verdicts plus an overall outcome, reusing the proposal-set shape (per-item ticks + Accept / Request changes / Reject)
- [ ] The verdict is written through `note_writes.py` into the design note's existing review fields — no new status vocabulary
- [ ] The verdict is **never auto-stamped**: the machine gathers, the human decides
- [ ] Requesting changes leaves the design in the queue with the per-region comments attached
- [ ] Accepting records what was accepted — which revision, which regions, on what date

## Steps

- [ ] Add designs to the queue intake states
- [ ] Reuse `buildSingleNoteReview`'s shape for per-region verdicts
- [ ] Extend the guarded writer's allow-list; no new fields beyond the review triple and the revision reference
- [ ] Test the accept and request-changes paths against a real design note

## Notes

Almost entirely reuse. FEAT-0041 already built the queue, the proposal-set review shape, the guarded write-back and 37 tests around it. A design review is the same interaction with regions in place of items.

"Accepting records which revision" matters more than it sounds: a verdict against v3 says nothing about v6, and a design surface that loses that distinction would let an old approval launder a new design. The revision reference is what stops that.
