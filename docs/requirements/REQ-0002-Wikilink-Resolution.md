---
type: "[[requirement]]"
id: REQ-0002
aliases: ["REQ-0002"]
title: "Resolves Obsidian-style [[wikilinks]] including project-os IDs"
status: approved
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
implemented_by: ["[[FEAT-0001]]"]
verified_by: []
---

# REQ-0002 — Wikilink resolution

Rendered pages SHALL resolve `[[Target]]` and `[[Target|Display]]` patterns to working HTML links pointing at the target note's URL. Resolution sources, in priority order:

1. Project-os ID match (`TASK-####`, `FEAT-####`, etc.) against the file index.
2. Frontmatter `id` field.
3. Frontmatter `aliases` list.
4. Filename (without extension) match.
5. H1 title within the file.

Targets that cannot be resolved SHALL render as a visually distinct "broken link" so the author sees them.

## Rationale
Project-os notes link heavily via wikilinks. Without this, every internal reference reads as plain text.
