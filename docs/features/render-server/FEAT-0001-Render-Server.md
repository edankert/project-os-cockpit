---
type: "[[feature]]"
id: FEAT-0001
aliases: ["FEAT-0001"]
title: "Markdown render server (frontmatter + wikilinks + on-the-fly)"
status: active
phase: "[[PHASE-001-MVP]]"
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
source: []
goal: "Render any .md note from a project-os repo as a linked HTML page on request — no build step — with frontmatter as metadata and [[wikilinks]] resolved across the whole tree."
release: ""
related: [FEAT-0002, FEAT-0004]
---

# Markdown render server

## Goal
A small Python HTTP server that, pointed at any project-os repo's `docs/` directory, serves every `.md` note as HTML at request time. No build step, no static-site generator, no dependency on Node. Frontmatter renders as a sidebar metadata strip; `[[wikilinks]]` resolve to the right pages via a pre-built title/ID/alias index.

## Scope
- **In scope:**
  - Stdlib HTTP server (`ThreadingHTTPServer`).
  - Markdown → HTML pipeline using the `markdown` library + a small set of `pymdownx` extensions (`tables`, `superfences`, `toc`, `fenced_code`).
  - YAML frontmatter parsing via `python-frontmatter`. Frontmatter renders as a metadata strip (status badge, owner, parent link, source list).
  - `[[wikilink]]` resolver supporting `[[Title]]`, `[[Title|Display]]`, `[[ID-####]]`, and frontmatter-defined aliases.
  - Auto-generated index pages by type and status.
  - Path-traversal guard: refuse to serve outside the configured docs root.
  - Shared HTML template with a brand-aligned CSS file (header, content area, sidebar, footer).
- **Out of scope:**
  - Live reload — covered by FEAT-0002.
  - Embedded terminal — covered by FEAT-0003.
  - Project-os-specific UI polish (status badges, structured backlinks panel) — covered by FEAT-0004.
  - Bases (`.base` files) rendering. They're plain YAML; the renderer treats them as raw text for now.
  - Search.

## Acceptance
- Pointed at this repo's `docs/`, the server returns 200 with rendered HTML for every `.md` under it.
- A note containing `[[FEAT-0001]]` renders a working link to `FEAT-0001-Render-Server.md`.
- Frontmatter (`status`, `owner`, `phase`, `parent`) renders as a visible metadata strip on every page.
- An auto-generated `/index/features` lists every feature grouped by status, with links.
- A request for `../../etc/passwd` (or equivalent traversal) returns 403, not file contents.

## Notes
This is the minimum-viable surface — once it can browse a project-os repo coherently, FEAT-0002 layers in live reload and FEAT-0003 layers in the terminal panel. FEAT-0004 polishes the project-os-aware UI bits.
