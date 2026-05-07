---
type: "[[phase]]"
id: PHASE-001
aliases: ["PHASE-001"]
title: "MVP"
status: active
order: 1
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
features:
  - "[[FEAT-0001-Render-Server]]"
  - "[[FEAT-0002-Live-Reload]]"
  - "[[FEAT-0003-Embedded-Terminal]]"
depends_on: []
---

# Phase 1: MVP

## Goal
The smallest useful tool: render any project-os repo's `docs/` tree as linked HTML, push live-reload events when files change, and expose a local-only embedded terminal panel for running an AI coding assistant alongside the docs.

Validated against this repo's own `docs/` (eat-our-own-dog-food).

## Scope

### In scope
- Markdown render server (FEAT-0001).
- Live reload via SSE (FEAT-0002).
- ttyd-iframe terminal panel, opt-in, loopback-only (FEAT-0003).

### Out of scope
- Project-os-specific UI polish (status badges, structured backlinks panel) — covered by PHASE-002.
- Downstream deployment in another repo — covered by PHASE-003.
- Search, graph view, full-text indexing — possible future phases.

## Exit criteria
- Running `python -m docs_server $(pwd)/docs` from this repo's root opens a working browser experience that:
  - Shows every `.md` rendered with frontmatter as metadata.
  - Resolves `[[wikilinks]]` correctly (TASK-#### / FEAT-#### / etc. all work).
  - Reloads pages within 1 second of an external editor saving the source file.
  - Shows the embedded terminal iframe on the host browser, hides it on a tablet on the LAN.

## Open decisions
- `tools/decisions/ADR-0003-*` — final install mechanism for downstream consumers (`pipx install -e ../docs-server` vs. running from source vs. submodule). Land before PHASE-003.
