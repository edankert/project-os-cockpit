---
type: "[[task]]"
id: TASK-0300
aliases: ["TASK-0300"]
title: "A ## Variant section with fenced html renders live, sandboxed, token-true"
status: backlog
phase: "[[PHASE-025-Design-Before-Code]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[FEAT-0067-Designs-Render-Their-Artefacts]]"]
parent: "[[FEAT-0067-Designs-Render-Their-Artefacts]]"
effort: M
depends: []
blocks: []
related: []
tests: []
---

# A ## Variant section with fenced html renders live, sandboxed, token-true

## Definition of Done

- The bench parses `## Variant <name>` fenced html into sandboxed iframes (`sandbox` without scripts unless the note's frontmatter opts in).
- The design-system stylesheet injects so mockups wear real tokens; a variant with none renders unstyled rather than failing.
