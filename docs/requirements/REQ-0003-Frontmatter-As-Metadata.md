---
type: "[[requirement]]"
id: REQ-0003
aliases: ["REQ-0003"]
title: "Surfaces YAML frontmatter as page metadata (status, owner, parent, etc.)"
status: approved
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
implemented_by: ["[[FEAT-0001]]"]
verified_by: []
---

# REQ-0003 — Frontmatter as metadata

Each rendered page SHALL surface the source file's YAML frontmatter as visible page metadata. At minimum: `status`, `owner`, `phase`, `parent`, `source`, `tags`. Frontmatter MUST NOT be rendered as inline body text.

The metadata strip is the project-os reader's primary "what is this and where does it sit" affordance — it doesn't need to be exhaustive in v1, but the high-signal fields above are required.

## Rationale
Project-os notes carry critical context in frontmatter (status, parent, links). Hiding it because Markdown renderers default to ignoring frontmatter would lose the project-os value-add.
