---
type: "[[issue]]"
id: ISS-0311
aliases: ["ISS-0311"]
title: "Exiting Codex closes the Electron cockpit instead of returning to the shell"
status: fixed
owner: user:edwin
created: 2026-09-15
updated: 2026-09-16
source: ["Edwin, 2026-09-15: when exiting codex it seems to exit from electron cockpit as well, which should not happen it should just exit back to the terminal"]
severity: high
component: desktop-terminal
phase: "[[PHASE-004-Embedded-Terminal]]"
parent: ""
related: ["[[FEAT-0003]]", "[[ISS-0310]]", "[[TASK-0627]]", "[[CHG-20260915-Fix-terminal-scrollback-and-Codex-exit-lifecycle]]", "[[CHG-20260916-Keep-cockpit-shell-open-after-Codex-exits]]", "[[CHG-20260916-Finish-PHASE-004-terminal-scrollback-and-Codex-exit]]"]
tests: ["tests/test_view_landings.py::test_a_terminal_child_exit_does_not_quit_the_electron_app", "desktop/tests/codex-shell-exit.test.mjs", "desktop/tests/terminal-history.test.mjs"]
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
- The current generated zsh wrapper invokes `command codex` inside a shell function. A source-text test checks its flags but does not run the shell, so it cannot prove that control returns to the prompt after the command exits.
- `desktop/tests/codex-shell-exit.test.mjs` now starts the generated zsh environment with a Codex stand-in. The stand-in exits with status 17, and the next command runs in the same shell process. This confirms the wrapper returns control after a child command exits; it does not prove the Electron window stays open in a live session.
- `desktop/tests/terminal-history.test.mjs` now simulates a PTY exit. The terminal backend sends `terminal:exit` to the renderer and does not call Electron quit.
- The 2026-09-16 isolated Electron walk started real Codex CLI 0.154.0 through the generated wrapper. Its `/exit` command returned to the shell. A later `printf` command ran in the same terminal, and the Electron window remained open ([[TASK-0627]]).
- No sibling issue was found for this exact child-exit-to-Electron-quit symptom; related terminal siblings [[ISS-0016]], [[ISS-0154]], [[ISS-0160]], [[ISS-0161]], and [[ISS-0310]] were searched by `terminal`, `scroll`, `mouse`, `codex`, `exit`, and `quit`.

## Impact analysis

This issue affects [[FEAT-0003]] and its [[REQ-0005]] requirement. The repair does not change the loopback-only terminal boundary or the xterm-plus-PTY architecture.

## Risk scan

No new dependency, environment variable, credential, directory, or network contract is introduced. The existing quit guard and tmux survivability behavior remain the boundary for app shutdown.

## Next Actions

- [x] Run a shell-level check that the generated Codex wrapper returns to the same shell after the Codex process exits.
- [x] Prove in the rebuilt Electron cockpit that a child command exit does not close the window.
- [x] Return to the shell prompt after Codex exits and run another command.
- [x] Walk Codex, Claude, and a plain shell in the rebuilt isolated cockpit.
