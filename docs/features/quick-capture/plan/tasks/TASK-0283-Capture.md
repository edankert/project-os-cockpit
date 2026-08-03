---
type: "[[task]]"
id: TASK-0283
aliases: ["TASK-0283"]
title: "⌘N capture — title in, triage issue out, current note linked, under three seconds"
status: backlog
phase: "[[PHASE-023-Levers-For-The-Human]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[FEAT-0061-Quick-Capture-And-Triage]]"]
parent: "[[FEAT-0061-Quick-Capture-And-Triage]]"
effort: S
depends: []
blocks: ["[[TASK-0284-The-Triage-Tray]]"]
related: ["[[TASK-0280-Create-Issue-And-The-Hardening-Suite]]"]
tests: []
---

# Capture

## Definition of Done

- ⌘N anywhere in a workspace opens the capture; Enter files it; Esc costs nothing.
- The issue lands at `triage` with `source:` naming the capture and `related:` the open note, and appears in the pane via the watcher without reload.
- The dialog never blocks on the sidecar: a failed create keeps the text and says why.
