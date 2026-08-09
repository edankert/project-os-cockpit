---
type: "[[task]]"
id: TASK-0368
aliases: ["TASK-0368"]
title: "The Tasks view retires in both front doors, with the stored-preference migration that already exists"
status: backlog
phase: "[[PHASE-022-Completed-Work-Gets-Quieter]]"
owner: user:edwin
created: 2026-08-09
updated: 2026-08-09
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
- [ ] `tasks` leaves the view set in **both** `renderer.ts` and `cockpit.js` — not one
- [ ] A stored preference of `tasks` migrates to `features`, via the existing `RETIRED_NAV_MODES` / fallback mechanism
- [ ] `_tasks_groups` is deleted, or the note records why it stays served
- [ ] Every task is still reachable: through its feature, or through the `Unattached tasks` group
- [ ] The find bar still locates a task by id

## Steps
- [ ] Add `tasks` to `RETIRED_NAV_MODES` with `features` as its fallback, in both renderers
- [ ] Remove the button and its icon branch
- [ ] Decide `_tasks_groups`' fate — it has no other consumer once the button is gone
- [ ] Check the stat tile: the overview's Tasks tile navigates to the `tasks` mode and must be repointed or it becomes a dead click ([[ISS-0063]] is that exact bug)

## Notes
**Both front doors, in the same change.** Retiring it in the shell alone would create a second `recent` — one view with two verdicts — which is the divergence [[FEAT-0084]] exists to remove. It is safe to do here precisely because the tree comes from the shared payload ([[TASK-0366]]), so mode 1 gains the nesting at the same moment it loses the flat list.

The stat-tile check is the one most likely to be missed: [[ISS-0063]] was three overview tiles that navigated nowhere, and retiring a mode is exactly how a live tile becomes a dead one.
