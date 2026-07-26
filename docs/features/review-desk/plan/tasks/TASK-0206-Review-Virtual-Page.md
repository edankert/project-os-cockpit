---
type: "[[task]]"
id: TASK-0206
aliases: ["TASK-0206"]
title: "~review virtual page — queue pane grouped Decisions/Proposals/Questions/Test runs, routing, Review mode button with count badge"
status: done
phase: "[[PHASE-008-State-And-Review-Surfaces]]"
owner: user:edwin
created: 2026-07-26
updated: 2026-07-26
source: ["https://claude.ai/code/artifact/3e6b4313-66e9-4fca-b11b-97c3d7a1d1be"]
parent: "[[FEAT-0041-Review-Desk]]"
effort: ""
due: ""
depends: []
blocks: ["[[TASK-0207]]", "[[TASK-0208]]", "[[TASK-0209]]"]
related: ["[[FEAT-0032-Agents-Screen]]", "[[FEAT-0034-Agents-Tab-And-Follow-Control]]", "[[TASK-0204]]"]
tests: []
---

# ~review virtual page

## Definition of Done

- [x] `~review` joins the virtual-page family (~overview, ~agents, ~session): history entries, follow-mode eviction guard (REQ-0020), footer path — the FEAT-0032/0034 patterns.
- [x] The left pane becomes the queue: groups Decisions / Proposals / Questions / Test runs with counts, rows typed (decide/review/answer/run), aged, and selectable; selection routes the stage (`~review/<ID>`, `~review/<TST-ID>/run`).
- [x] Queue sources: `status: proposed` ADRs, `draft` requirements/plans, and `ready` manual tests via their existing intake states; the FEAT/TASK Proposals group is driven by **dispatch-ledger review requests**, not status filters — pending-ness is runtime queue state and the notes stay at plain `backlog` (ADR-0007 mechanism, owner decision 2026-07-26); Questions come from ledger question entries.
- [x] The Review mode button occupies the slot Active/Recent vacate (TASK-0204), with a queue-count badge; the badge clears as items are handled and follows REQ-0018's no-decay principle (unhandled items keep counting).
- [x] Empty state designed ("Nothing waiting on you") — the audit's quiet-first rule applies here too.

## Steps

- [x] Page shell + routing + history + follow guard (copy the ~agents pattern).
- [x] Queue derivation over the index + ledger; group/sort/age rendering.
- [x] Mode button + badge wiring; deep-link targets for TASK-0210's overview rows.

## Notes

The stage content for each queue kind lands in TASK-0207 (proposals/decisions), TASK-0208 (questions), TASK-0209 (test runs); this task ships the shell, queue, routing, and badge with simple note-preview stages as placeholders where needed.
