---
type: "[[issue]]"
id: ISS-0154
title: "Existing terminal sessions stop receiving keyboard input after a workspace switch"
status: "fixed"
owner: user:edwin
created: 2026-08-12
updated: "2026-08-13"
source: ["Edwin report 2026-08-12"]
severity: high
component: desktop-terminal
parent: ""
related: ["[[FEAT-0003-Embedded-Terminal]]", "[[ISS-0016-Embedded-Terminal-Content-Runs-Off-Screen-And-Mouse-Scroll-Stops-Working-After-Switching-To-The-Console]]", "[[TASK-0186-Terminal-Force-Resize-On-Show]]"]
tests: []
---

# Existing terminal sessions stop receiving keyboard input after a workspace switch

## Problem

Long-running CLI sessions in the desktop cockpit become unable to react to keyboard input after the user leaves their workspace and returns. A newly created/opened terminal accepts keys initially, but the same session stops accepting them after the next workspace round-trip. This makes already-running Claude Code, Codex, and other interactive CLIs appear frozen even though their PTY remains alive.

## Repro

1. Open the desktop cockpit and show the terminal pane.
2. In workspace A, start or attach to an interactive CLI and verify normal keyboard input works.
3. Switch to workspace B while the terminal pane remains open.
4. Return to workspace A and attempt to type into the existing CLI.
5. Repeat with a newly created terminal: it accepts input at first, then fails after leaving and returning.

## Expected

Whenever a visible terminal is attached to the active workspace, its xterm textarea has keyboard focus (unless the user deliberately focused another editable control), and keystrokes route to that workspace's live PTY.

## Actual

The initial open/spawn path accepts input. Existing sessions after a workspace switch do not react to key presses.

## Evidence

- `desktop/src/renderer/renderer.ts:907` calls `void attachTerminalTo(id)` during `openWorkspace()` when the terminal is already visible, but does not restore `term.focus()` after the asynchronous attachment.
- In contrast, `showTerminal()` and `restartTerminal()` explicitly schedule `term.focus()` after their attach/resize flow (`desktop/src/renderer/renderer.ts:2762`, `2825`). This matches the reported difference between a freshly opened terminal and a revisited one.
- `attachTerminalTo()` changes `attachedTerminalId`, resets the one shared xterm, and awaits a spawn/attach (`desktop/src/renderer/renderer.ts:2684-2725`). Rapid workspace changes can interleave those asynchronous reattachments; verify that no stale completion replays data, geometry, or focus for a no-longer-active workspace.
- The existing mouse-input repair [[ISS-0016-Embedded-Terminal-Content-Runs-Off-Screen-And-Mouse-Scroll-Stops-Working-After-Switching-To-The-Console]] establishes the same architectural boundary: one xterm is reused across workspace PTYs and switching resets its state.

## Next Actions

- [ ] Reproduce against two live CLI sessions and inspect `document.activeElement`, `attachedTerminalId`, and `terminal:input` IPC while switching A → B → A.
- [ ] Make workspace attachment ordered/cancellable and restore keyboard focus only after the winning active-workspace attachment completes.
- [ ] Add a renderer-level regression test that exercises visible-terminal workspace switching and proves typed bytes reach the returning workspace's PTY, not merely that its backlog renders.

## Fixed — 2026-08-13

Both halves, and the second was the one the issue predicted rather than observed.

**The keyboard.** `showTerminal` and `restartTerminal` each scheduled `term.focus()` after their attach; `openWorkspace` — the path a *switch* takes — did not. That is exactly the reported difference: a freshly opened console takes keys, the same console after A→B→A does not. All three now go through `attachAndFocusTerminal`, which re-checks that the workspace is still active and the pane still open before taking focus, so a slow attach cannot yank the caret out of something you started typing meanwhile.

**The race.** `attachedTerminalId` is assigned synchronously and the attach is awaited, so A→B→A could let B's backlog land in the terminal now showing A. A generation token now guards every await — the same shape as [[TASK-0187]]'s PTY identity guard and [[ISS-0158]]'s duplicated band, which is three of this family in one file.

**Guards, mutation-checked**: `test_every_terminal_attach_restores_the_keyboard` asserts nothing calls the bare attach, and `test_the_terminal_attach_cannot_replay_a_stale_backlog` asserts every await re-checks. Reverting either fix fails its own test.
