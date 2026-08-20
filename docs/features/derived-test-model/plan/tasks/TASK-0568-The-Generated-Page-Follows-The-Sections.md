---
type: "[[task]]"
id: TASK-0568
aliases: ["TASK-0568"]
title: "The generated page: sections instead of tiers, and Automated tests without checkboxes"
status: done
phase: "[[PHASE-039-A-Test-Says-Who-Executes-It]]"
owner: user:edwin
created: 2026-08-19
updated: "2026-08-20"
source: []
parent: "[[FEAT-0140-Sections-Are-Derived-Not-Filed]]"
effort: "M"
due: ""
depends: []
blocks: []
related: []
tests: []
---

# The generated page: sections instead of tiers, and Automated tests without checkboxes

## Definition of Done
- [ ] `~checks` renders section then area then items
- [ ] Automated tests renders no checkbox and no todo count
- [ ] Order within a section is unchanged from [[TASK-0556]]

## Steps
- [ ] Replace the tier loop in `view_payload`
- [ ] Suppress the checkbox and the todo tally for the automated section
- [ ] Leave area order and in-area order alone

## Notes

[[TASK-0556]] settled the ordering and the reason: this page is where the suite is completed, and a list that reorders as you tick things is one you lose your place in. Sections change; order does not.

A tickbox beside something no person executes is what put nine automated checks into `your-trainer`'s blocking 68.
