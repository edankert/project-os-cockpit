---
type: "[[phase]]"
id: PHASE-002
aliases: ["PHASE-002"]
title: "Project-os adapter"
status: done
order: 2
owner: user:edwin
created: 2026-05-07
updated: 2026-07-20
features:
  - "[[FEAT-0004-Project-OS-Adapter]]"
  - "[[FEAT-0006-Cockpit-Layout]]"
depends: ["[[PHASE-001-MVP]]"]
---

# Phase 2: Project-os adapter

## Goal
Polish the rendering for project-os specifically: status badges from frontmatter, parent-link breadcrumbs, structured backlinks panel, auto-index pages following the project-os taxonomy, *and* a bases-driven 3-pane cockpit layout that mirrors Edwin's Obsidian workflow in the browser. Turn the basic renderer into a project-os dashboard.

## Scope

### In scope
- Status badges (colour-coded chips for every status across the taxonomy).
- Parent-link breadcrumbs derived from `parent:` fields.
- Backlinks panel listing notes that link to the current page, grouped by note type.
- Surfacing `SNAPSHOT.yaml` `focus` on the landing page.
- Cross-repo references rendered as plain links without breaking page rendering.
- **Bases-driven 3-pane cockpit (FEAT-0006):** any `.base` file mountable as a pane, JSON API + vanilla-JS client renderer, `this.file` propagation for right-pane re-evaluation on active-note change, SSE-driven re-fetch on edits.

### Out of scope
- Edit-via-web (read-only stays read-only).
- Full-text search.

## Exit criteria
- A FEAT-#### note's rendered page shows: status badge, breadcrumb, backlinks list.
- `/index/features` and friends are usefully grouped and linked.
- Landing page surfaces `focus.task` / `focus.feature` / `focus.phase` from SNAPSHOT.
- Default cockpit (NAV.base left / rendered note centre / CONTEXT.base right) works against this repo's own `docs/`; non-default cockpits (any `.base` in any pane via CLI flags) work without code changes.

## Dependencies
PHASE-001 must be complete before this starts — there's no project-os adapter to layer onto without a working renderer.

## Close-out (2026-07-20)

All in-scope work is complete: the adapter's ID-resolution / status-badge / backlink scope shipped as core cockpit capability (FEAT-0006 + the index/render layer); FEAT-0004 was superseded on that basis. No open items remain in this phase.
