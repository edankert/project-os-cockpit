---
type: "[[task]]"
id: TASK-0124
aliases: ["TASK-0124"]
title: "Session history browser — list + detail view"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-05
updated: 2026-07-05
parent: "[[FEAT-0022-Session-Insight-And-Traceability]]"
effort: "M"
depends: ["[[TASK-0123]]"]
blocks: []
related: []
tests: []
---

# Session history browser

## Definition of Done
- [ ] A read-only Sessions surface per workspace lists past sessions: prompt summary, agent, duration, cost, files touched.
- [ ] Selecting a session opens a detail view (metadata + prompt list + touched files, each file linkable when under `docs/`).
- [ ] Graceful empty state when no sessions are recorded.

## Steps
- [ ] Fetch `/api/cockpit/sessions`; list UI (library nav group or dedicated pane section).
- [ ] Detail view rendering in the centre pane.
- [ ] Link touched docs files through the existing rel-path navigation.

## Notes
v1 is metadata + prompt summaries; full transcript rendering is a follow-up.
