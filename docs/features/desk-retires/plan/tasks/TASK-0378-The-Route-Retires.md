---
type: "[[task]]"
id: TASK-0378
aliases: ["TASK-0378"]
title: "~review, its mode and its button go, with the migration that stops a stored preference stranding the reader"
status: backlog
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-10
updated: 2026-08-10
source: ["[[FEAT-0090-The-Desk-Retires]]"]
parent: "[[FEAT-0090-The-Desk-Retires]]"
effort: M
due: ""
depends: ["[[TASK-0377-The-Registers-Re-Home]]"]
blocks: []
related: ["[[FEAT-0084-One-View-Vocabulary]]", "[[ISS-0063-Dead-Stat-Tiles]]"]
tests: ["[[TST-0022-Surface-Ownership]]"]
---

# The route retires

## Definition of Done
- [ ] Every row of [[ADR-0020]]'s re-homing table is reachable at its new home — **walked**, not inspected
- [ ] `~review`, the `review` mode and its button are gone; a stored preference or deep link migrates
- [ ] The overview's Tests stat tile navigates somewhere live
- [ ] `review_queue_payload` and the desk renderers are deleted, or the note records why they stay
- [ ] The review ledger and its store are untouched
- [ ] A test asserts the badge total equals the registry total with no desk present
- [ ] [[TST-0022]]'s desk steps are rewritten, and it passes

## Steps
- [ ] Walk the re-homing table item by item and record the walk
- [ ] Retire the mode in both renderers via `RETIRED_NAV_MODES` — one view, one verdict, per [[FEAT-0084]]
- [ ] Re-point the Tests tile
- [ ] Delete the payload and renderers; keep `review.py`'s store

## Notes
**Retire in both front doors or neither.** Mode 1 has no Review button today, so this is mostly mode 3 — but the view set is the thing [[FEAT-0084]] is single-sourcing, and leaving a half-retired mode is how `recent` ended up with two verdicts.

[[ISS-0063]] is the stat-tile bug in its exact form: retiring a mode is how a live tile becomes a dead click, and the Tests tile points at `~review` today.

The badge-equals-registry assertion is the one that makes removal provable rather than asserted — it is the whole reason this task comes last.
