---
type: "[[task]]"
id: TASK-0167
aliases: ["TASK-0167"]
title: "Terminal context menu + ⌘C/⌘V + copy-on-select setting"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-19
updated: 2026-07-19
source: []
parent: "FEAT-0037"
effort: ""
due: ""
depends: ["[[TASK-0166]]"]
blocks: []
related: []
tests: []
---

# TASK-0167 — terminal context menu

xterm needs its own menu (decision: right-click opens the menu even with a selection — Mac convention; copy-on-select is the opt-in for the PuTTY-inclined): **Copy** (enabled on `term.hasSelection()`), **Paste** (clipboard → PTY write, bracketed-paste wrapping for multi-line so a pasted script doesn't execute line-by-line), **Select All**, **Clear**. Keyboard: ⌘C copies the selection when one exists (falls through to SIGINT otherwise), ⌘V pastes. `copyOnSelect` joins the app settings popover. Verification: select output → right-click Copy → paste elsewhere; multi-line paste arrives as one bracketed block; ⌘C with no selection still interrupts.
