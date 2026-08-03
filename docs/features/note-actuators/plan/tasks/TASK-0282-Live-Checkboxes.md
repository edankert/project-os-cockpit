---
type: "[[task]]"
id: TASK-0282
aliases: ["TASK-0282"]
title: "Criteria checkboxes tick from the note view, with an inline evidence prompt and the reconcile form behind a menu"
status: backlog
phase: "[[PHASE-023-Levers-For-The-Human]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[FEAT-0060-Transitions-And-Ticks-On-The-Note]]"]
parent: "[[FEAT-0060-Transitions-And-Ticks-On-The-Note]]"
effort: M
depends: ["[[TASK-0281-The-Action-Row]]"]
blocks: []
related: ["[[TASK-0279-The-Tick-Path]]"]
tests: []
---

# Live checkboxes

## Definition of Done

- Unticked boxes in criteria sections are clickable only where the server reports the tick action legal for this note.
- Click opens an inline evidence field ("what shows this is met?"); submit calls the tick path; the row re-renders from the file.
- Reconcile (`[~]` + reason) reachable from the same affordance's menu.
- A stale-mtime refusal surfaces as "note changed — reloaded", never as silence.
