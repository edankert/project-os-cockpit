---
type: "[[feature]]"
id: FEAT-0090
aliases: ["FEAT-0090"]
title: "The desk retires — its registers re-home, its route migrates, and nothing that lived on it becomes unreachable"
status: planned
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-10
updated: 2026-08-10
source: ["[[ADR-0020-Obligations-Live-With-Their-Subject]]"]
goal: "Remove ~review once every obligation it carried has a home, moving the reviewed register to the record surfaces and migrating the route, so the removal is provable rather than asserted."
requirements: []
tasks:
  - "[[TASK-0377-The-Registers-Re-Home]]"
  - "[[TASK-0378-The-Route-Retires]]"
release: ""
related: ["[[ADR-0020-Obligations-Live-With-Their-Subject]]", "[[FEAT-0041-Review-Desk]]", "[[FEAT-0049-Review-Desk-As-Record]]", "[[ISS-0121-Reviewed-Register-Counts-Settled-Work-As-Owed]]", "[[FEAT-0084-One-View-Vocabulary]]"]
tests: []
---

# The desk retires

## Goal

`~review` goes last, and only once [[FEAT-0089]]'s registry can demonstrate that every kind it carried has an owner. Removing it first would be a leap; removing it last is bookkeeping.

## What it still holds when its turn comes

- **The reviewed register** — 103 verdicts. A record, not an obligation ([[ADR-0020]] decision 7), so it joins the record surfaces beside ADRs, changes and designs.
- **The tests register and the runner** — gone to [[FEAT-0086]] before this starts.
- **The route** `~review`, plus the mode, its button, its stored preference and any deep link.

## Scope

**In:** moving the reviewed register; retiring the route, mode and button with the migration `RETIRED_NAV_MODES` already provides; deleting `review_queue_payload` and the desk renderers once nothing calls them; re-pointing the overview's Tests stat tile, which navigates to `~review` today.

**Out:**

- The review *ledger* and its store. The mechanism that records a review request and its outcome is [[ADR-0007]]'s and survives; only its display goes. Deleting the store would destroy the record of what the desk decided.
- Questions. [[ADR-0020]] decision 6 drops the surface, not the ledger kind.
- [[ISS-0121]]'s fix — it is a member of this phase and lands with the register move, because relocating a register that counts settled work as owed would relocate the defect.

## Acceptance

- [ ] Every row of [[ADR-0020]]'s re-homing table is demonstrably reachable at its new home — walked, not inspected
- [ ] The reviewed register renders among the record surfaces, and no longer reports settled work as owed
- [ ] `~review`, its mode and its button are gone from the shell; a stored preference or deep link migrates rather than stranding the reader
- [ ] The overview's Tests tile navigates somewhere live ([[ISS-0063]] is exactly this bug)
- [ ] `review_queue_payload` and the desk renderers are deleted, or the note records why they stay
- [ ] The review ledger and store are untouched
- [ ] A test asserts the badge total equals the registry total with no desk present — the invariant that made removal safe

## Links

- Decision: [[ADR-0020-Obligations-Live-With-Their-Subject]]
- Coordination: [[FEAT-0084]] wants the view set single-sourced; retiring a view is a view-set change, so whichever lands second must not restate the other's list
- Paths: `src/project_os_cockpit/cockpit.py` (`review_queue_payload`, `_reviewed_register`), `src/project_os_cockpit/server.py`, `desktop/src/renderer/renderer.ts` (`renderReviewPage`, `renderReviewQueuePane`)
