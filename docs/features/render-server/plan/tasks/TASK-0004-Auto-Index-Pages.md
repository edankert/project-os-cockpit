---
type: "[[task]]"
id: TASK-0004
aliases: ["TASK-0004"]
title: "Auto-generated index pages (features, tasks, requirements, etc. by status)"
status: backlog
phase: "[[PHASE-001-MVP]]"
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
source: []
implements: ["[[FEAT-0001]]", "[[REQ-0007]]"]
fixes: []
effort: S
due: ""
depends: [TASK-0003]
blocks: []
related: []
tests: []
---

# Auto-index pages

## Definition of Done
- [ ] `GET /index/features` returns a list of every FEAT-* note grouped by status, with links.
- [ ] Same for `/index/tasks`, `/index/requirements`, `/index/issues`, `/index/risks`, `/index/decisions`, `/index/changes`, `/index/releases`, `/index/workflows`, `/index/tests`, `/index/phases`.
- [ ] Landing page (`/`) lists each index type with a count.
- [ ] Each grouped section is collapsible and ordered: active/doing/in_progress first, backlog/triage middle, done/closed/verified last.

## Steps
- [ ] `index.py`: extend the index built in TASK-0003 to capture frontmatter `type` + `status` per file.
- [ ] Add `GET /index/<type>` route handler that filters the index and renders a grouped list.
- [ ] Template helper for status-grouped lists.
- [ ] Wire the landing page to render counts per type.

## Notes
Unlike FEAT-0004's adapter polish (status badges, parent breadcrumbs, etc.), this task only needs the listing. Visual polish lands in PHASE-002.
