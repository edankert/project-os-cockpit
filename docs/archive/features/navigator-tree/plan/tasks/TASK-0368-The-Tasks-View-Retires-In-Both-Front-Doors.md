---
type: "[[task]]"
id: TASK-0368
aliases: ["TASK-0368"]
title: "The Tasks view retires in both front doors, with the stored-preference migration that already exists"
status: done
phase: "[[PHASE-022-Completed-Work-Gets-Quieter]]"
owner: user:edwin
created: 2026-08-09
updated: 2026-08-10
source: ["[[FEAT-0085-The-Navigator-Shows-The-Structure-The-Record-Has]]"]
parent: "[[FEAT-0085-The-Navigator-Shows-The-Structure-The-Record-Has]]"
effort: S
due: ""
depends: ["[[TASK-0366-Tasks-Join-Their-Feature]]", "[[TASK-0367-Task-Children-Sort-By-Status-And-Fold]]"]
blocks: []
related: ["[[FEAT-0084-One-View-Vocabulary]]", "[[TASK-0365-Recent-Gets-One-Verdict]]"]
tests: []
---

# The Tasks view retires in both front doors

## Definition of Done
- [x] `tasks` leaves the view set in **both** front doors — button removed from `index.html`, entry removed from `cockpit.js`'s `NAV_MODES`; guarded by `test_design_sits_second_before_the_structure_modes`
- [x] A stored preference of `tasks` migrates to `features` via `RETIRED_NAV_MODES` and the fallback map
- [x] `_tasks_groups` **stays served**, and the module records why — see below
- [x] Every task is still reachable — asserted against the real corpus rather than by inspection: the palette test now walks the features payload and fails if any of the 384 is unreachable
- [x] The find bar still locates a task by id — same assertion; and see the deduplication below
- [x] The overview's Tasks stat tile repointed to `features` ([[ISS-0063]]'s exact bug)

## Steps
- [x] Add `tasks` to `RETIRED_NAV_MODES` with `features` as its fallback
- [x] Remove the button from `index.html` and the entry from `cockpit.js`
- [x] Decide `_tasks_groups`' fate — retained for API stability, reason recorded in the module
- [x] Repoint the stat tile (both the project and scoped overviews carried one)

## Notes
**Both front doors, in the same change.** Retiring it in the shell alone would create a second `recent` — one view with two verdicts — which is the divergence [[FEAT-0084]] exists to remove. It is safe to do here precisely because the tree comes from the shared payload ([[TASK-0366]]), so mode 1 gains the nesting at the same moment it loses the flat list.

The stat-tile check is the one most likely to be missed: [[ISS-0063]] was three overview tiles that navigated nowhere, and retiring a mode is exactly how a live tile becomes a dead one.

## The endpoint stays; the button goes

`nav_payload(mode="tasks")` remains served. That is [[FEAT-0008]]'s API-stability commitment, and the same reason `active` and `recent` kept their endpoints when TASK-0204 took their buttons: **a retired button is a UI decision; deleting an endpoint is a contract change**, and nothing here needed one.

## Found while retiring: the palette would have doubled

`QUICK_CORPUS_MODES` listed `features` **and** `tasks`. `flattenNavItems` descends into `children` — so once [[TASK-0366]] put tasks under their feature, `features` alone already carried all 384, and keeping `tasks` would have added every one of them to Cmd+P a second time.

Removing it deduplicates the palette *and* preserves the coverage claim. The guarding test was rewritten to assert what it actually cares about — that every task is reachable — against the live payload, rather than a list of mode names. **A test that checks the mechanism goes stale the moment the mechanism changes; one that checks the property does not.**
