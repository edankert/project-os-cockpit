---
type: "[[requirement]]"
id: REQ-0008
aliases: ["REQ-0008"]
title: "Backlinks panel showing notes that link to the current page"
status: verified
phase: "[[PHASE-002-Project-OS-Adapter]]"
implements: ["[[FEAT-0006]]"]
owner: user:edwin
created: 2026-05-07
updated: 2026-05-23
implemented_by: ["[[FEAT-0004]]"]
verified_by: []
tests: ["[[TST-0001]]"]
---

# REQ-0008 — Backlinks panel

Every rendered page SHALL include a "Backlinks" section listing notes that link to it (via `[[wikilinks]]`, frontmatter ID references, or `parent:` chains).

Backlinks SHALL be grouped by source-note type (Features / Tasks / Requirements / etc.) when the count is high enough to benefit, otherwise listed flat.

## Rationale
Backlinks expose dependencies that aren't visible from the note itself. A risk that's referenced from three features is more important than one that's orphaned; a feature that's the parent of ten tasks deserves different treatment than one with two.

## Verification
- 2026-05-23: marked `verified` — Backlinks panel shipped in the cockpit right pane (TASK-0007); covered by TST-0001.
