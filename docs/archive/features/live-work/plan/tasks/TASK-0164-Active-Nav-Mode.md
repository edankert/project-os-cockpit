---
type: "[[task]]"
id: TASK-0164
aliases: ["TASK-0164"]
title: "'Active' nav mode — in-flight items only, live row migration, default for phase-less projects"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-19
updated: 2026-07-19
source: []
parent: "FEAT-0036"
effort: ""
due: ""
depends: ["[[TASK-0162]]"]
blocks: []
related: []
tests: []
---

# TASK-0164 — Active nav mode

New left-pane mode (joins overview/features/tasks/issues/library/recent; mockup: round-2 artifact §4 option B): only in-flight items across all types, grouped **Doing / Next / Done today**, ordered by recent activity; an "agent" chip on rows a live session's `docs_notes` contains; rows migrate between groups on `cockpit:status-change` (no full-pane reload — targeted moves, brief highlight). Server side: `mode=active` in `/api/cockpit/nav`. When the project has no `docs/phases/`, Active becomes the default landing mode instead of the empty overview. Verification: flip statuses in a fixture repo — rows migrate live; phase-less project lands on Active; agent chip appears while a session touches the note.
