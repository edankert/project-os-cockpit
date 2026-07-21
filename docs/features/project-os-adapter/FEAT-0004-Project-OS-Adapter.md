---
type: "[[feature]]"
id: FEAT-0004
aliases: ["FEAT-0004"]
title: "Project-os adapter (ID resolution, status badges, backlinks)"
status: superseded
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-07
updated: 2026-07-20
source: []
goal: "Make the rendered output project-os-aware: status badges, parent-link breadcrumbs, structured backlinks panel, and auto-index pages that match the project-os taxonomy."
release: ""
related: ["[[FEAT-0001]]", "[[FEAT-0005]]", "[[REQ-0012]]"]
---

# Project-os adapter

## Goal
Once the basic renderer (FEAT-0001) works, polish the rendering for project-os specifically: status chips from the frontmatter `status:` field, parent-link breadcrumbs (`parent: "[[FEAT-0008]]"` → breadcrumb to FEAT-0008), structured backlinks panel showing notes that link in, and auto-index pages following the project-os taxonomy (`/index/features` grouped by status, `/index/tasks` grouped by parent feature, etc.).

All UI added by this feature follows the visual contract in [[REQ-0012]] — muted greyscale base, semantic-only color, both themes.

## Scope
- **In scope:**
  - Status chips for `active`, `doing`, `done`, `verified`, `blocked`, `backlog`, `triage`, `closed`. Hues are perceptually distinct but desaturated per [[REQ-0012]] — no traffic-light brightness. Chip tokens are CSS custom properties, defined once and reused in both themes.
  - Parent-link breadcrumbs, derived from `parent:` in frontmatter.
  - Structured backlinks panel: every page lists which other notes link to it. Built from a reverse-link index that's invalidated by the file watcher.
  - Auto-index pages: `/index/features`, `/index/tasks`, `/index/requirements`, `/index/issues`, `/index/risks`, `/index/decisions`, `/index/changes`, `/index/releases`, `/index/workflows`, `/index/tests`, `/index/phases`. Each grouped by status by default; query params override the grouping.
  - Cross-repo references: `../your-applications.com/...` style frontmatter sources rendered as plain links (or skipped on render-time errors) without breaking the page.
  - Read SNAPSHOT.yaml at startup; surface its `focus.task` / `focus.feature` / `focus.phase` on the landing page.
- **Out of scope:**
  - Bases (`.base` files) — kept as plain text for now; if rendering becomes valuable, separate feature.
  - Edit-via-web (read-only viewer; editing happens in your editor or in the embedded terminal).
  - Full-text search — separate feature.
  - Graph view (Obsidian-style node graph).

## Acceptance
- A FEAT-#### note's rendered page shows: status chip rendered with the muted accent palette, breadcrumb (`Feature › <title>`), and a backlinks section listing every note that links to it. Chips render correctly in both light and dark themes.
- `/index/features` returns a grouped list (Active / Doing / Backlog / Done) with each item linked to its detail page.
- The landing page shows the current focus from `SNAPSHOT.yaml` if one is set.
- A note with `parent: "[[FEAT-0008]]"` shows "Parent: [[FEAT-0008]]" rendered as a working link in the metadata strip.

## Notes
This is what turns the renderer from "browseable Markdown" into "project-os dashboard". The work is mostly templating + indexing on top of FEAT-0001's pipeline.

## Superseded (2026-07-20)

The adapter's scope — ID resolution, status badges, backlinks — shipped as core cockpit capability: the index provides ID/alias/backlink resolution and the renderer draws status badges (FEAT-0006 + the index/render work). No distinct adapter layer is needed, so this feature is superseded by [[FEAT-0006-Cockpit-Layout]].
