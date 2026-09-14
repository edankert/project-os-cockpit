---
type: "[[task]]"
id: TASK-0625
aliases: ["TASK-0625"]
title: "~checks groups by screen, with a dialog's checks under the screen it opens from, following the template's surface rules and the same parent lookup the walk sheet uses"
status: backlog
phase: "[[PHASE-044-The-Walk-Page-Reads-As-A-Script]]"
owner: user:edwin
created: 2026-09-14
updated: 2026-09-14
source: ["[[FEAT-0150-The-Walk-Page-Reads-As-A-Script]]", "project-os-dev ADR-0044"]
parent: "[[FEAT-0150-The-Walk-Page-Reads-As-A-Script]]"
effort: M
due: ""
depends: []
blocks: []
related: ["[[FEAT-0130-Surfaces-Are-A-First-Class-Type]]", "[[FEAT-0114-The-Suite-Is-A-View]]", "[[TASK-0556-Incomplete-First]]", "[[ISS-0250-A-Surface-Rename-Silently-Orphans-Its-Checks]]"]
tests: []
tags: [task, acceptance, checks, renderer]
---

# ~checks groups by screen

## Why

`~checks` groups rows by section, then `area:`, then id. Once your-trainer's surfaces are screens with dialogs as children (its TASK-0901, TASK-0902), a flat list of areas puts "HR-zone interval sheet" nowhere near "Workout editor". The template's rules put a child under its parent; this page should too.

## Definition of Done

- [ ] `view_payload` groups by top-level screen, with each child surface as a subgroup, using `parent:` from the surface notes.
- [ ] The parent lookup is the bundled module's, not a second implementation, so the page and the walk sheet cannot disagree about which screen a dialog belongs to.
- [ ] `subsystem` and `surface-less` surfaces render as their own groups after the screens.
- [ ] Owed rows still float to the top of their group, and nothing reorders on a tick (TASK-0556).
- [ ] A surface with no checks still renders, and its count is still on the design view (FEAT-0130).
- [ ] An `area:` naming no surface still renders visibly, not silently dropped (ISS-0250).
- [ ] Tests on a fixture with a parent screen, a child dialog and a subsystem.
