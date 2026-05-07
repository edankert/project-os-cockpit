---
type: "[[requirement]]"
id: REQ-0008
aliases: ["REQ-0008"]
title: "Backlinks panel showing notes that link to the current page"
status: approved
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
implemented_by: ["[[FEAT-0004]]"]
verified_by: []
---

# REQ-0008 — Backlinks panel

Every rendered page SHALL include a "Backlinks" section listing notes that link to it (via `[[wikilinks]]`, frontmatter ID references, or `parent:` chains).

Backlinks SHALL be grouped by source-note type (Features / Tasks / Requirements / etc.) when the count is high enough to benefit, otherwise listed flat.

## Rationale
Backlinks expose dependencies that aren't visible from the note itself. A risk that's referenced from three features is more important than one that's orphaned; a feature that's the parent of ten tasks deserves different treatment than one with two.
