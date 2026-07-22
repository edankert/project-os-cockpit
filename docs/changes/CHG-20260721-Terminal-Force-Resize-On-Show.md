---
type: "[[change]]"
id: CHG-20260721-Terminal-Force-Resize-On-Show
title: "Restore per-workspace mouse-tracking mode on console re-attach so wheel scrolling survives a workspace switch"
date: 2026-07-22
author: user:edwin
status: merged
related: ["[[ISS-0016]]", "[[TASK-0186]]", "[[TASK-0185]]", "[[FEAT-0003]]"]
reviewed_by: "opus-independent-review"
review_date: 2026-07-22
review_verdict: CLOSE
---

# CHG-20260721 — restore mouse-tracking mode on console re-attach

## What changed

`attachTerminalTo` in `desktop/src/renderer/renderer.ts` now snapshots the leaving workspace's `term.modes.mouseTrackingMode` before `term.reset()`, and on return (after the backlog replay) re-asserts the saved mode by writing its DECSET enable sequence + `?1006h` (SGR encoding) to xterm. `showTerminal` became async and awaits the attach before calling `forceRefitTerminal` (a genuine resize round-trip on show). The `XtermTerminal` interface gained `resize(cols, rows)` and `modes`.

## Why

The embedded console's mouse-wheel scroll was dead right after switching to it, until a manual divider drag. Live CDP instrumentation traced the real cause (not xterm scrollback, as first assumed): one xterm is shared across workspaces, so a workspace switch calls `term.reset()`, which wipes xterm's mode state — including `mouseTrackingMode`. The console apps (Claude Code / TUIs) run in the alternate-screen buffer with mouse tracking on and rely on xterm forwarding wheel events to the PTY; after the reset, xterm's mode is `none`, the raw-byte backlog ring buffer can't restore it (the enable sequence predates the buffer), and the app only re-emits it on its next redraw — so the wheel stayed dead until then. The divider drag worked only because the resize prompted a redraw. Restoring the mode directly makes it deterministic.

## Impact

- **Behaviour**: returning to a previously-visited Claude console scrolls immediately with the wheel — no manual resize. A plain shell keeps `none` and thus its native scrollback scrolling. The first visit to a workspace in a session (no snapshot yet) still relies on the app's redraw. Confirmed working live by the user.
- **Scope**: renderer-only; requires a desktop rebuild — done, `tsc` clean. The DECSET is written to xterm only (changes xterm's mode, not the PTY).
- **Also included**: `showTerminal` awaits the attach before the force-resize (so the SIGWINCH can't precede the reset), and `forceRefitTerminal` + the earlier `ResizeObserver` (TASK-0185) keep the content-not-clipped fix.

## Files

- `desktop/src/renderer/renderer.ts` — per-workspace `workspaceMouseMode` snapshot/restore in `attachTerminalTo`; async `showTerminal` ordering; `forceRefitTerminal`; `XtermTerminal` gains `resize`/`modes`.
