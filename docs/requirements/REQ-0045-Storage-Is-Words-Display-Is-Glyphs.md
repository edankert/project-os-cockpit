---
type: "[[requirement]]"
id: REQ-0045
aliases: ["REQ-0045"]
title: "The mark is stored as a word and displayed as a check mark, and no surface may render the stored form"
status: approved
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
priority: medium
scope: "acceptance surfaces"
implements: "[[FEAT-0126-A-Rendered-Mark-Is-A-Check-Mark]]"
acceptance:
  - "[ ] Every surface that shows a mark renders it through one map; none reads `mark` directly."
  - "[ ] A guard fails if a raw mark word (`done`, `todo`, `canceled`, …) reaches a rendered surface."
  - "[ ] Storage is unchanged: the notes still carry words, per ISS-0200."
covers: []
related: ["[[ISS-0211-The-Mark-Picker-Shows-Words-Where-The-Check-Mark-Was]]", "[[ISS-0200-Marks-Versus-Statuses]]"]
tags: [requirement]
---

# Storage is words; display is check marks

Edwin: *"this is where I would like to see the check marks and not the states."*

The two are not in tension — the file wants an unambiguous token and the screen wants a checklist — and treating them as one field is what produced `[done]` rendered beside the label `Done`.

Criterion 2 is the one with teeth. Criteria 1 and 3 describe today's fix; the guard is what makes it hold, because the failure mode here is not a wrong rendering but a **silent** one: of the three sites, one was a dead comparison that removed styling and one was a `title` attribute.

## Acceptance criteria

- [ ] One map, no direct reads.
- [ ] A guard on raw words reaching a surface.
- [ ] Storage unchanged.
