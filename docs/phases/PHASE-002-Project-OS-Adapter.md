---
type: "[[phase]]"
id: PHASE-002
aliases: ["PHASE-002"]
title: "Project-os adapter"
status: backlog
order: 2
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
features:
  - "[[FEAT-0004-Project-OS-Adapter]]"
depends_on: ["[[PHASE-001-MVP]]"]
---

# Phase 2: Project-os adapter

## Goal
Polish the rendering for project-os specifically: status badges from frontmatter, parent-link breadcrumbs, structured backlinks panel, and auto-index pages following the project-os taxonomy. Turn the basic renderer into a project-os dashboard.

## Scope

### In scope
- Status badges (colour-coded chips for every status across the taxonomy).
- Parent-link breadcrumbs derived from `parent:` fields.
- Backlinks panel listing notes that link to the current page, grouped by note type.
- Surfacing `SNAPSHOT.yaml` `focus` on the landing page.
- Cross-repo references rendered as plain links without breaking page rendering.

### Out of scope
- Bases (`.base` files) rendering — separate future phase.
- Edit-via-web (read-only stays read-only).
- Full-text search.

## Exit criteria
- A FEAT-#### note's rendered page shows: status badge, breadcrumb, backlinks list.
- `/index/features` and friends are usefully grouped and linked.
- Landing page surfaces `focus.task` / `focus.feature` / `focus.phase` from SNAPSHOT.

## Dependencies
PHASE-001 must be complete before this starts — there's no project-os adapter to layer onto without a working renderer.
