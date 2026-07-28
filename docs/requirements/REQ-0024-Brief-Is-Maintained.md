---
type: "[[requirement]]"
id: REQ-0024
aliases: ["REQ-0024"]
title: "The project brief is a maintained artifact, not a template stub"
status: draft
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["measurement:2026-07-28 — 10 of 11 fleet repos carry an unfilled LLM_BRIEF.md"]
priority: medium
scope: "Every project states what it is and what it is for, in a file an agent reads and a validator checks."
acceptance:
  - "This repo's LLM_BRIEF.md carries no REPLACE ME placeholders"
  - "A brief still carrying placeholders is reported by validate-docs"
  - "The design surface renders the brief, and says plainly when it is unfilled rather than displaying the placeholder"
  - "The brief remains readable and editable as plain Markdown without the cockpit"
implements: "[[FEAT-0043-Design-Top-Level-Surface]]"
verifies: []
related: []
tests: []
---

# The brief is maintained

## Statement

Every project **shall** state what it is and what it is for in `LLM_BRIEF.md`, and that file **shall** be checked rather than assumed.

## Rationale

Measured across the fleet on 2026-07-28: **10 of 11 repos carry `Name: REPLACE ME` and `Purpose: REPLACE ME`** — including `project-os` itself, `project-os-cockpit` with its 42 features, and four shipped applications. The single exception was created the previous day by an agent that happened to be reading the template.

Two failures compound here and both need fixing:

1. **Nothing shows it.** The cockpit has never referenced `LLM_BRIEF.md`. A file with no surface has no feedback loop, and a template stub survives indefinitely because nothing ever confronts anyone with it.
2. **Nothing checks it.** `validate-docs` reports dangling links, drifted statuses and unresolved assets, but never noticed that eleven projects failed to say what they are.

The second is the cheaper fix and the more damning omission.

## Acceptance Criteria

- [ ] This repo's `LLM_BRIEF.md` has no `REPLACE ME` — evidence: <grep>
- [ ] A placeholder brief is reported by the validator — evidence: <check + inversion>
- [ ] The surface says "unfilled" rather than rendering the placeholder — evidence: <test>
- [ ] The brief stays plain Markdown, editable without the cockpit — evidence: <the file>

## Traceability
- Implements: [[FEAT-0043-Design-Top-Level-Surface]]
- Verified by: `tools/scripts/validate-docs.py` and the design-surface tests
