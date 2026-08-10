---
type: "[[feature]]"
id: FEAT-0090
aliases: ["FEAT-0090"]
title: "The desk retires — its registers re-home, its route migrates, and nothing that lived on it becomes unreachable"
status: done
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

- [x] Every row of [[ADR-0020]]'s re-homing table is demonstrably reachable at its new home — walked against the live corpus, nine rows, table in [[TASK-0378]]
- [x] The reviewed register renders among the record surfaces, and no longer reports settled work as owed — 104 verdicts, **0 owed** ([[TASK-0377]])
- [~] `~review`, its mode and its button are gone from the shell; a stored preference or deep link migrates rather than stranding the reader — **the mode and the button are gone and migrate to `overview`; the route stays served**, because the agent ledger has one OPEN entry and [[ISS-0126]] owns where those flows land
- [x] The overview's Tests tile navigates somewhere live ([[ISS-0063]] is exactly this bug) — and the guard now renders the destination rather than naming a mode, after the Risks tile spent a commit pointing at a pane its type had left
- [~] `review_queue_payload` and the desk renderers are deleted, or the note records why they stay — **they stay, for the same one open entry**; reachable from the record column's link and nowhere else
- [x] The review ledger and store are untouched — asserted
- [x] A test asserts the badge total equals the registry total with no desk present — `test_the_badges_still_total_the_registry_with_no_desk`

## Links

- Decision: [[ADR-0020-Obligations-Live-With-Their-Subject]]
- Coordination: [[FEAT-0084]] wants the view set single-sourced; retiring a view is a view-set change, so whichever lands second must not restate the other's list
- Paths: `src/project_os_cockpit/cockpit.py` (`review_queue_payload`, `_reviewed_register`), `src/project_os_cockpit/server.py`, `desktop/src/renderer/renderer.ts` (`renderReviewPage`, `renderReviewQueuePane`)

## Closed 2026-08-10

**The desk is dissolved as a place and kept as a door.** Its button is gone, its mode migrates, and every register and queue group is answered by the view that owns its subject. What survives is a route with one caller: the record column links to it while the agent ledger has an open request, and this repo has exactly one.

That is a reconciliation, not a completion, and the reason is a measurement rather than a preference. Retiring the route today would have stranded a live entry a human is expected to act on — the trap `RETIRED_NAV_MODES` exists to prevent, one level up. Where proposals, questions and offered designs land is [[ISS-0126]], which this release names as Edwin's decision and tells the session not to guess at. When it is answered, deleting the route is a small change with nothing behind it.

**Two rows of the table are empty in this corpus** — no `proposed` design, no manual test at `ready` — so they are asserted by their *view owning the kind* rather than by having rows. A kind that is empty today is indistinguishable from a kind that does not exist, which is how `change` and `release` went missing from the registry in the first place ([[ISS-0128]]).

The invariant that made removal safe holds: **the badge total equals the sum of the badges, and every declared owing kind has a view that exists.** That is the whole of what the desk's one number used to do, now checkable.
