---
type: "[[phase]]"
id: PHASE-001
aliases: ["PHASE-001"]
title: "MVP"
status: done
order: 1
owner: user:edwin
created: 2026-05-07
updated: 2026-05-08
features:
  - "[[FEAT-0001-Render-Server]]"
  - "[[FEAT-0002-Live-Reload]]"
depends_on: []
---

# Phase 1: MVP

## Goal
The smallest useful tool: render any project-os repo's `docs/` tree as linked HTML and push live-reload events when files change.

Validated against this repo's own `docs/` (eat-our-own-dog-food).

## Scope

### In scope
- Markdown render server (FEAT-0001).
- Live reload via SSE (FEAT-0002).

### Out of scope
- Embedded terminal — moved to [[PHASE-004-Embedded-Terminal]] so PHASE-001 could close on the genuinely-MVP renderer + live-reload combination.
- Project-os-specific UI polish (status badges, structured backlinks panel) — covered by [[PHASE-002-Project-OS-Adapter]].
- Downstream deployment in another repo — covered by [[PHASE-003-Downstream-Pilot]].
- Search, graph view, full-text indexing — possible future phases.

## Exit criteria (met 2026-05-08)
- Running `python -m project_os_cockpit $(pwd)/docs` from this repo's root opens a working browser experience that:
  - Shows every `.md` rendered with frontmatter as metadata. ✓
  - Resolves `[[wikilinks]]` correctly (TASK-#### / FEAT-#### / etc. all work). ✓
  - Reloads pages within 1 second of an external editor saving the source file. ✓ (~100 ms)

## Open decisions
- `tools/decisions/ADR-0003-*` — final install mechanism for downstream consumers (`pipx install -e ../project-os-cockpit` vs. running from source vs. submodule). Land before PHASE-003.
