---
type: "[[task]]"
id: TASK-0163
aliases: ["TASK-0163"]
title: "Session rail 'work' tab — status boxes per touched note, filling live as the agent closes items"
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

# TASK-0163 — session "work" tab

In the session rail next to "files" (mockup: round-2 artifact §4 option A): a mini row of status boxes — one per docs note in the session's `docs_notes` (TASK/ISS/FEAT/REQ ids), filled when that note's status is terminal (done/fixed/verified bucket, same semantics as the overview squares), accent-filled while doing. Boxes update live on `cockpit:status-change`. The expanded detail gains tabs: **work** (item list with live status chips, click → navigate) | **files** (existing list). Verification: drive a session touching two tasks; flip one to done → its box fills within a second; expanded list chip updates; files tab unchanged.
