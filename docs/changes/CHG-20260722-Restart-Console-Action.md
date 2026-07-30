---
type: "[[change]]"
id: CHG-20260722-Restart-Console-Action
title: "Add a Restart console action to recover a wedged terminal (kills PTY + tmux session, respawns)"
date: 2026-07-22
author: user:edwin
status: merged
related: ["[[ISS-0017]]", "[[TASK-0187]]", "[[TASK-0144]]", "[[FEAT-0003]]"]
reviewed_by: "opus-independent-review"
review_date: 2026-07-22
review_verdict: ""
---

# CHG-20260722 — Restart console action

## What changed

Added a "Restart console" item to the terminal context menu (`desktop/src/renderer/renderer.ts`). It calls the existing `terminal:dispose` IPC for the active workspace — which `killPty`s the PTY and, for tmux-backed terminals, also kills the backing tmux session — then clears the renderer's `liveTerminals`, `workspaceMouseMode`, and `attachedTerminalId` state and re-attaches via `attachTerminalTo`, spawning a fresh shell in place. A `window.confirm` guards the destructive kill.

## Why

A workspace console can wedge with no in-app recovery: a TUI stuck on a picker, a hung pager, a broken PTY. Because the terminal is tmux-backed (TASK-0144, survives app restarts), restarting the app just reconnects to the same stuck session — the only escape was manually killing the tmux session from a shell. This surfaced when the your-health console got stuck on Claude Code's resume-session picker (ISS-0017). No user-facing control existed over `terminal:dispose`/`terminal:spawn`, which were already implemented.

## Impact

- **Behaviour**: right-click the console → Restart console (after confirming) kills the current shell + its tmux session and starts a fresh one in the same pane. Reuses existing, tested IPC; no new main-process surface.
- **Destructive by design**: it kills whatever runs in the console (including a live Claude/codex session), hence the confirm. Intended as a recovery escape hatch.
- **Scope**: renderer-only; requires a desktop rebuild — done, `tsc` clean.

## Files

- `desktop/src/renderer/renderer.ts` — `restartTerminal()` + "Restart console" context-menu item.

## Review verdict cleared — 2026-07-30

`review_verdict` read **`CLOSE`**, which is not a value QUALITY.md defines (`approved` | `changes-requested`). Cleared per [[ISS-0069]], on the principle that a verdict nobody can interpret is not a verdict and should not satisfy a gate.

**What is deliberately kept:** `reviewed_by: "opus-independent-review"` and `review_date`. A review demonstrably happened, by a named reviewer, on that date — that is real information and clearing it would destroy evidence rather than correct a claim. Only the uninterpretable value is gone.

The consequence is intended: this note is now `merged` without a verdict, so [[ADR-0011]]'s REVIEW warning applies to it like anything else unreviewed, with the same 2026-10-23 deadline. It joins an honest backlog instead of reading as a satisfied gate.
