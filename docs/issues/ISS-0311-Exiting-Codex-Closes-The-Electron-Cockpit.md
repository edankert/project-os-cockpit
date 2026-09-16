---
type: "[[issue]]"
id: ISS-0311
aliases: ["ISS-0311"]
title: "Exiting Codex closes the Electron cockpit instead of returning to the shell"
status: open
owner: user:edwin
created: 2026-09-15
updated: 2026-09-15
source: ["Edwin, 2026-09-15: when exiting codex it seems to exit from electron cockpit as well, which should not happen it should just exit back to the terminal"]
severity: high
component: desktop-terminal
phase: "[[PHASE-004-Embedded-Terminal]]"
parent: ""
related: ["[[FEAT-0003]]", "[[ISS-0310]]", "[[TASK-0627]]", "[[CHG-20260915-Fix-terminal-scrollback-and-Codex-exit-lifecycle]]"]
tests: ["tests/test_view_landings.py::test_a_terminal_child_exit_does_not_quit_the_electron_app"]
---

# Exiting Codex closes the Electron cockpit

## Problem

Ending the interactive Codex child should return control to the shell inside the embedded terminal. Instead, the Electron cockpit appears to close at the same time, which loses the terminal host rather than ending only the child command.

> [!quote] As reported — 2026-09-15 (Edwin)
> when exiting codex it seems to exit from electron cockpit as well, which should not happen it should just exit back to the terminal

## Repro

1. Open the Electron cockpit and show the embedded terminal.
2. Start the interactive `codex` command in the workspace.
3. End the Codex session using its normal exit action.
4. Observe the terminal and the Electron window.

## Expected

Codex exits, the shell prompt remains visible in the embedded terminal, and the Electron cockpit stays open.

## Actual

The cockpit appears to exit together with Codex instead of leaving the user at the shell prompt.

## Evidence

- `desktop/src/ipc/terminal.ts` owns the PTY child and emits `terminal:exit` when it exits.
- `desktop/src/main.ts` owns Electron quit handling and should only run it for an app/window quit, not for a child command exit.
- No sibling issue was found for this exact child-exit-to-Electron-quit symptom; related terminal siblings [[ISS-0016]], [[ISS-0154]], [[ISS-0160]], [[ISS-0161]], and [[ISS-0310]] were searched by `terminal`, `scroll`, `mouse`, `codex`, `exit`, and `quit`.

## Impact analysis

This issue affects [[FEAT-0003]] and its [[REQ-0005]] requirement. The repair does not change the loopback-only terminal boundary or the xterm-plus-PTY architecture.

## Risk scan

No new dependency, environment variable, credential, directory, or network contract is introduced. The existing quit guard and tmux survivability behavior remain the boundary for app shutdown.

## Next Actions

- [ ] Prove that a child command exit only updates the terminal and does not close the Electron window.
- [ ] Return to the shell prompt after Codex exits.
- [ ] Walk Codex, Claude, and a plain shell in the rebuilt cockpit.
