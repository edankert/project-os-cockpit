---
type: "[[task]]"
id: TASK-0300
aliases: ["TASK-0300"]
title: "A ## Variant section with fenced html renders live, sandboxed, token-true"
status: done
phase: "[[PHASE-025-Design-Before-Code]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
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

## Done — 2026-08-11

`## Variant <name>` + a fenced ```html block, parsed server-side (`design_variants`) and rendered into `srcdoc` iframes.

**Convention over machinery, as the feature's goal asks.** A variant is a markdown section, so an agent or a human authors one with what they already have — no new note type, no editor, no upload path.

**Sandboxed WITHOUT `allow-scripts` unless the note opts in** via `scripts: true`. The artifact frame allows scripts because DES-0001 carries a theme toggle and a script-free sandbox would break the acceptance subject; a fragment fenced inside a note has not earned that. The opt-in lives in the note's frontmatter rather than in the renderer, so it is a recorded per-design decision rather than a blanket allowance.

The design-system stylesheets inject through the existing `/design-asset/` route, so mockups wear real tokens — and a variant whose note declares none **renders unstyled rather than failing**, because an unstyled shape still answers *which arrangement*, which is what a variant is for.

Two parsing rules, each with a test: a `##` of any kind ends the section (otherwise the last variant swallows the rest of the note), and **only the first fence in a section counts** — a variant is one shape, and a section with two fences has not decided.
