---
type: "[[feature]]"
id: FEAT-0036
aliases: ["FEAT-0036"]
title: "Live work views — watch tasks/features/issues move: session work tab, Active nav mode, phase-less Now board"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-19
updated: 2026-07-20
reviewed_by: "model:claude-opus"
review_date: 2026-07-20
review_verdict: approved
goal: "The cockpit stops being a static snapshot: a status-diff layer turns note saves into transition events (TASK-0157 doing→done), feeding (a) a 'work' tab in the session rail — one status box per docs note this session touched, filling live as the agent closes items, expandable to a chip list; (b) an 'Active' left-pane nav mode showing only in-flight items across types (Doing / Next / Done today, agent chips, live row migration) — also the default landing view for phase-less projects where the overview has nothing to say; (c) later, a full-width Now board replacing the empty phase grid on the overview."
requirements: []
tests: []
tasks: ["[[TASK-0162]]", "[[TASK-0163]]", "[[TASK-0164]]", "[[TASK-0165]]"]
related: ["[[FEAT-0020-Agent-Activity-Surfaces]]", "[[FEAT-0023-Overview-Scopes]]", "[[FEAT-0030-Agent-Inbox]]"]
---

# Live work views

## Why

User feedback 2026-07-19: the overview works poorly for phase-less projects and everything is static — "it would be great if we had another option which would show the current set of tasks/features/requirements/issues being worked on and would show them being done." Mockups: round-2 artifact §4 (options A + B recommended, C as follow-on).

## Scope

- **TASK-0162 — status-diff layer (foundation).** The sidecar watcher already fires per note save; add a frontmatter-status differ that emits `cockpit:status-change {id, rel, type, from, to, ts}` over SSE and records a capped recent-transitions log. Everything below renders this stream; the attention panel's finished log can consume it too.
- **TASK-0163 — session "work" tab.** In the session rail next to "files": mini status boxes (▣▣▢) for the docs notes this session touched (tracker `docs_notes`), filled when their status turns terminal; expanded view lists items with live status chips; same square language as the overview.
- **TASK-0164 — Active nav mode.** Left-pane mode: in-flight items only, across all types, grouped Doing / Next / Done-today, ordered by recent activity, "agent" chip on rows a live session touched, rows migrating between groups on status-change events. Default landing mode when the project has no phases.
- **TASK-0165 — phase-less Now board (follow-on).** Overview centre renders the same data full-width (columns + animated transitions) when `docs/phases/` is empty, replacing the empty phase grid.

## Out of scope

Kanban drag-and-drop (statuses change through the docs/agents, not the board); cross-workspace aggregation (that's ~agents).
