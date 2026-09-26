---
type: "[[task]]"
id: TASK-0241
aliases: ["TASK-0241"]
title: "Tests register on the desk — every acceptance test, not the runnable slice"
status: done
phase: "[[PHASE-010-Surface-Ownership]]"
owner: user:edwin
created: 2026-07-29
updated: 2026-07-29
source: []
parent: "[[FEAT-0049-Review-Desk-As-Record]]"
effort: M
depends: []
blocks: ["[[TASK-0245-Drop-Relocated-Groups]]"]
related: ["[[ISS-0063-Dead-Stat-Tiles]]", "[[TASK-0211-Verification-Panel]]"]
tests: ["[[TST-0022-Surface-Ownership]]"]
---

# TASK-0241 — Tests register

## Definition of Done
- [ ] `review_queue_payload` carries a `registers.tests` block with every `[[test]]` note
- [ ] Each entry: id, title, status, `last_verified`, manual/automated, staleness
- [ ] Count equals `index.notes_by_type("test")` — 21 here, not the ~4 in the "Test runs" queue group
- [ ] Rendered beneath the queue in the desk's left pane, visually separated from it
- [ ] The overview's Tests stat tile navigates to `~review`

## Steps
- [ ] Add the register to `review_queue_payload` in `cockpit.py`, independent of the `_is_manual_test` / `ready` gating the queue uses
- [ ] Reuse `_slim_note` for entry shape
- [ ] Renderer: a `Tests` section under the queue groups in `renderReviewQueuePane`
- [ ] Pass `'review'` as the Tests tile's `navMode` (`renderer.ts:5236`)
- [ ] Test: register count equals the corpus test count; queue group count stays gated

## Notes

The queue group and the register must stay distinct. "Test runs" answers "what is waiting on me", the register answers "what do we verify". Collapsing them would lose the queue's meaning and make the desk's badge count wrong.

The per-scope Verification panel ([[TASK-0211]]) is untouched.
