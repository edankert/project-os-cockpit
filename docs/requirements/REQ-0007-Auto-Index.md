---
type: "[[requirement]]"
id: REQ-0007
aliases: ["REQ-0007"]
title: "Auto-generated index pages by status / parent / type"
status: verified
phase: "[[PHASE-001-MVP]]"
implements: ["[[FEAT-0001]]"]
owner: user:edwin
created: 2026-05-07
updated: 2026-05-23
implemented_by: ["[[FEAT-0001]]", "[[FEAT-0004]]"]
verified_by: []
---

# REQ-0007 — Auto-generated index pages

The render server SHALL provide auto-generated index pages for every project-os note type at `/index/<type>` (e.g. `/index/features`, `/index/tasks`, `/index/requirements`, `/index/risks`, `/index/decisions`, `/index/changes`, `/index/releases`, `/index/issues`, `/index/workflows`, `/index/tests`, `/index/phases`).

Each index page SHALL group items by status (active/doing first, backlog/triage middle, done/closed last). Each item SHALL link to its detail page.

## Rationale
A user shouldn't need to walk the directory tree to find every feature, every open issue, every active risk. The index pages give the project-os taxonomy a first-class browsing path.

## Verification
- 2026-05-23: marked `verified` — Auto-index routes shipped (/index/<type>) via TASK-0004 / CHG-20260507-Auto-Index-Pages.
