---
type: "[[issue]]"
id: ISS-0017
aliases: ["ISS-0017"]
title: "No way to recover a stuck/broken console (e.g. a TUI wedged on a picker) — need a restart action"
status: fixed
severity: medium
owner: user:edwin
created: 2026-07-22
updated: 2026-07-22
source: ["user-report"]
related: ["[[FEAT-0003]]", "[[TASK-0187]]"]
---

# ISS-0017 — no way to restart a stuck console

## Symptom

A workspace console (your-health) became wedged on Claude Code's resume-session picker and could not be exited via the keyboard. Because the terminal is tmux-backed (TASK-0144, survives app restarts), restarting the app just reconnects to the same stuck session. There was no in-app way to kill and respawn a console.

Trigger in this instance: stray keystrokes were injected into the console during an unrelated CDP diagnosis session, which navigated Claude's launcher into a state it wouldn't advance out of. But the general gap stands — any console can wedge (a runaway TUI, a hung pager, a broken PTY) with no recovery short of manually killing the tmux session from a shell.

## Fix

See [[TASK-0187]]: a "Restart console" action (terminal context menu) that disposes the active workspace's PTY — which also kills its backing tmux session (killPty) — clears the renderer's live-terminal + saved-mouse-mode state, and re-attaches, spawning a fresh shell in place.
