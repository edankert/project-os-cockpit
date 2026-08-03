---
type: "[[task]]"
id: TASK-0284
aliases: ["TASK-0284"]
title: "The triage tray — accept-as-severity or decline on every row, siblings hinted, investigation one dispatch away"
status: backlog
phase: "[[PHASE-023-Levers-For-The-Human]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[FEAT-0061-Quick-Capture-And-Triage]]"]
parent: "[[FEAT-0061-Quick-Capture-And-Triage]]"
effort: M
depends: ["[[TASK-0283-Capture]]"]
blocks: []
related: ["[[TASK-0278-The-Transition-Table-As-Data]]"]
tests: []
---

# The triage tray

## Definition of Done

- `Needs triage · N` renders above the open severities when N > 0, in the card grammar; absent when empty.
- Accept-as-severity writes severity + `open` through the transition path; decline writes `declined`. Both leave the tray in one click plus at most one pick.
- Rows with word-overlapping open issues show the sibling id inline.
- The row's menu offers dispatch-to-agent with the issue as subject (existing dispatch machinery).
