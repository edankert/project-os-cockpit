---
type: "[[requirement]]"
id: REQ-0049
aliases: ["REQ-0049"]
title: "A surface exists whether or not a test names it, and the suite groups by a controlled vocabulary"
status: draft
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
priority: medium
scope: "surfaces"
implements: "[[FEAT-0130-Surfaces-Are-A-First-Class-Type]]"
acceptance:
  - "[ ] A surface is a note. It exists, and is listed, with zero tests naming it."
  - "[ ] The consolidated set for your-trainer is small enough to hold in the head — a target of 12-15, not 76 — and every original area maps onto one, with the mapping recorded rather than inferred."
  - "[ ] Surfaces are visible on the design view, beside the other things that bound the project."
  - "[ ] No check loses its history in the consolidation: the original `area:` string is preserved on the note."
covers: []
related: ["[[DES-0012-Tests-In-Two-Flows]]"]
tags: [requirement]
---

# A surface exists on its own

Criterion 4 is the constraint on criterion 2. Consolidating 76 strings into ~13 is a **lossy rename** unless the original is kept — and the original is the only evidence of what a check was originally filed under. `your-trainer`'s suite is 579 notes; a mapping applied without preserving the source is not reversible by reading.

Criterion 1 is the whole point of the type. A string cannot be absent; a note can.

## Acceptance criteria

- [ ] A surface exists with zero tests.
- [ ] A consolidated set of 12-15, mapping recorded.
- [ ] Visible on the design view.
- [ ] The original `area:` preserved.
