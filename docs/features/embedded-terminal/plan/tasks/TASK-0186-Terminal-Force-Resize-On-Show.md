---
type: "[[task]]"
id: TASK-0186
aliases: ["TASK-0186"]
title: "Fix: restore per-workspace mouse-tracking mode on console re-attach so wheel scrolling survives a workspace switch"
status: done
phase: "[[PHASE-004-Embedded-Terminal]]"
owner: user:edwin
created: 2026-07-21
updated: 2026-07-22
source: ["[[ISS-0016]]"]
parent: "FEAT-0003"
effort: ""
due: ""
depends: ["[[TASK-0185]]"]
blocks: []
related: []
tests: []
verification_waiver: "Renderer-only terminal-mode wiring; xterm mouse-forwarding has no automated renderer unit-test surface. Diagnosed with live CDP instrumentation (captured xterm's mouseTrackingMode flipping to 'none' on switch-in) and confirmed working live by the user after the deterministic mode-restore landed; independent review on the code."
---

# TASK-0186 — restore mouse-tracking mode on console re-attach

Follow-up to [[TASK-0185]] / [[ISS-0016]]. The dead mouse-wheel scroll was NOT an xterm-scrollback problem. Live instrumentation showed the real chain: the cockpit shares ONE xterm across workspaces, and switching workspaces calls `term.reset()` in `attachTerminalTo`, which wipes xterm's mode state — including `mouseTrackingMode`. The apps in the console (Claude Code and other TUIs) run in the alternate-screen buffer with mouse tracking on (`?1003h`), so scrolling is the app's own, driven by xterm forwarding wheel events to the PTY in mouse mode. After a switch, xterm's `mouseTrackingMode` is `none` (reset), the raw backlog ring buffer can't restore it (the enable sequence long predates the buffer), and the app only re-emits it on its next redraw — so the wheel is dead until then. Dragging the divider "fixed" it only because the resize prompted the app to redraw.

Fix (deterministic, not timing-dependent): snapshot each workspace's `term.modes.mouseTrackingMode` when leaving it, and on return — after `reset()` + backlog replay — re-assert it by writing the matching DECSET enable sequence (plus `?1006h` SGR encoding) to xterm. A plain shell stays `none`, so xterm keeps forwarding wheel to its own native scrollback; a Claude/codex TUI restores to `any`, so wheel forwarding resumes immediately. Supporting changes: `showTerminal` now awaits the attach before the resize (so the SIGWINCH can't race ahead of the reset), and `forceRefitTerminal` sends a genuine resize on show (helps a first-visit redraw and keeps [[TASK-0185]]'s clip fix). Added `resize`/`modes` to the `XtermTerminal` type.

Verification: confirmed live by the user — returning to a previously-visited Claude console scrolls immediately without a manual drag. Known edge: the very first visit to a workspace in a session has no snapshot yet, so it still relies on the app's redraw; a broader follow-up could restore the full mode set (bracketed paste, app cursor keys) that reset() also wipes.
