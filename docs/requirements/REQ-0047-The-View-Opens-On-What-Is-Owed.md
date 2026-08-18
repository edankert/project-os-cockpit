---
type: "[[requirement]]"
id: REQ-0047
aliases: ["REQ-0047"]
title: "The tests view opens on what is owed and what has moved, with the inventory one click away"
status: approved
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
priority: medium
scope: "tests view"
implements: "[[FEAT-0128-The-Tests-View-Leads-With-The-Work]]"
acceptance:
  - "[ ] The landing state of the tests view is not a list of every test. On a 579-test repo the reader sees groups and counts, not rows."
  - "[ ] Each tier reports walked, needing re-run, and still to walk — derived, never authored."
  - "[ ] Nothing is removed: every collapsed group expands to exactly the rows it collapsed."
  - "[ ] Feature tests appear above the flat state groups."
covers: []
related: ["[[ADR-0028]]", "[[ISS-0204-The-Acceptance-Filter-Bar-Is-Congested]]"]
tags: [requirement]
---

# Owed first, inventory on request

The view was built when the corpus had 23 tests, where showing all of them WAS the summary. At 579 it is a wall, and the same change that made it a wall — [[PHASE-035]]'s migration — also gave every row a state worth counting.

**Criterion 3 is the constraint on the other three.** The easy version of this feature deletes rows; the correct one moves them behind a summary that says how many there are. Every count must expand to its own rows, or the collapse has hidden work rather than organised it.

## Acceptance criteria

- [ ] The landing state is not the inventory.
- [ ] Per-tier walked / re-run / to-walk, derived.
- [ ] Every collapsed group expands losslessly.
- [ ] Feature tests lead.
