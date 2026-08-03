---
type: "[[task]]"
id: TASK-0280
aliases: ["TASK-0280"]
title: "Issue creation from template with the next free id, and the mutation-grade hardening suite over all three verbs"
status: backlog
phase: "[[PHASE-023-Levers-For-The-Human]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[FEAT-0059-The-Write-Service-Widens]]"]
parent: "[[FEAT-0059-The-Write-Service-Widens]]"
effort: M
depends: ["[[TASK-0278-The-Transition-Table-As-Data]]"]
blocks: []
related: ["[[RISK-0005-The-Write-Surface]]"]
tests: []
---

# Create, and the hardening suite

## Definition of Done

- `POST /api/notes/create` (type=issue): fills the issue template, id = index max + 1 (sync-snapshot's counter confirms at pre-commit, same number), status `triage` unless severity given, links carried from the payload.
- Filename follows the corpus convention; the watcher picks the file up and SSE announces it — the pane updates without reload.
- The hardening suite: every refusal exercised — non-loopback caller, agent-owned transition, unknown field, stale mtime, path traversal, duplicate id race. Each guard broken once to prove the suite bites (the PHASE-022 lesson, applied from day one).
