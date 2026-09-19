---
type: "[[task]]"
id: TASK-0627
aliases: ["TASK-0627"]
title: "Keep terminal scrolling usable and keep the cockpit open when Codex exits"
status: done
phase: "[[PHASE-004-Embedded-Terminal]]"
owner: user:edwin
created: 2026-09-15
updated: 2026-09-16
source: ["[[ISS-0310]]", "[[ISS-0311]]"]
parent: "FEAT-0003"
effort: ""
due: ""
depends: []
blocks: []
related: ["[[TASK-0186]]", "[[ISS-0016]]", "[[ISS-0154]]", "[[ISS-0160]]", "[[ISS-0161]]", "[[SUR-0002]]", "[[CHG-20260916-Make-Codex-terminal-history-scrollable-through-tmux]]", "[[CHG-20260916-Keep-tmux-scrolling-after-workspace-reattachment]]", "[[CHG-20260916-Trial-Codex-alternate-screen-display-in-the-Electron-console]]", "[[CHG-20260916-Revert-ineffective-Codex-alternate-screen-trial]]", "[[CHG-20260916-Keep-cockpit-shell-open-after-Codex-exits]]"]
tests: ["tests/test_agent_instrument.py::test_codex_wrapper_preserves_terminal_scrollback", "tests/test_view_landings.py::test_the_terminal_restores_mouse_mode_only_for_an_alternate_buffer", "tests/test_view_landings.py::test_a_normal_terminal_buffer_can_scroll_past_stale_tui_mouse_mode", "tests/test_view_landings.py::test_the_console_wheel_and_history_action_reach_tmux", "tests/test_view_landings.py::test_tmux_history_survives_workspace_reattachment", "tests/test_view_landings.py::test_a_terminal_child_exit_does_not_quit_the_electron_app", "desktop/tests/terminal-history.test.mjs", "desktop/tests/codex-shell-exit.test.mjs"]
---

# Keep terminal scrolling usable and keep the cockpit open when Codex exits

## Definition of Done

- [x] Wheel input reaches the normal shell's tmux history after Codex has run. The isolated Electron walk moved the first visible line from `HISTORY_LINE_105` to `HISTORY_LINE_090`.
- [x] The console History action opened tmux copy mode. A real wheel gesture then moved within that history.
- [x] After switching to a second workspace and back, a real wheel gesture moved the first visible line from `HISTORY_LINE_096` to `HISTORY_LINE_081`.
- [x] Reattachment queries tmux's mouse-request state. The focused backend and renderer checks pass, and the live shell returned with mouse tracking off.
- [x] Claude kept its alternate screen and mouse tracking after switching away and back. A wheel gesture left its tmux pane on the alternate screen with mouse input enabled.
- [x] The generated Codex wrapper kept its notification flag and `--no-alt-screen`. Real Codex `/exit` returned to the shell, and the next shell command ran while the Electron window stayed open.
- [x] Focused Node and Python checks cover the wheel path, wrapper exit, and PTY child-exit separation.
- [x] The isolated rebuilt Electron desktop ran a plain shell, Codex CLI 0.154.0, and Claude Code 2.1.271.

## Steps

- [x] Trace and repair xterm wheel handling for normal and alternate buffers, preserving Claude's behavior and launching Codex in inline mode.
- [x] Expose tmux history in the Electron console and route wheel events according to the inner pane's screen and mouse state.
- [x] Verify that PTY child exit notifications remain local to the terminal renderer; the Node check observed `terminal:exit` without Electron quit.
- [x] Run the generated Codex wrapper in a real shell and check that the same shell accepts another command after Codex exits.
- [x] Preserve the existing Codex notification wrapper while adding `--no-alt-screen`, and add regression coverage for the wrapper.
- [x] Trial Codex's alternate-screen display, compare its scrolling with the baseline, and revert it after no change was observed.

## Notes

Sibling search found the earlier dimension, keyboard handoff, stale mouse-mode, backlog replay, and Codex scrollback issues. The new work joins their shared terminal path but does not widen [[REQ-0005]] or add a new runtime dependency.

The 2026-09-16 review found that tmux itself enters xterm's alternate screen on attach ([[ISS-0161]]). Codex's `--no-alt-screen` flag cannot make xterm use its normal buffer through that outer tmux client. The explicit History action must work even when an interactive program captures the mouse. Automatic wheel routing uses the inner tmux pane's alternate-screen state, so programs such as Claude keep their existing input behavior. tmux mouse handling remains off to preserve selection in xterm.

Edwin's live walk found that returning to a project sometimes changed the wheel from full tmux history to short or empty xterm scrollback. The renderer had required xterm's alternate-buffer state, but `term.reset()` and a capped PTY replay cannot always reconstruct that state. Wheel routing now uses the workspace's tmux backing independently of xterm's reconstructed buffer. Whether Codex should keep its prompt fixed like Claude is a separate choice about Codex's own display mode.

The alternate-screen trial did not change what Edwin saw. Process arguments confirmed that Codex received `tui.alternate_screen="always"`, while tmux reported `alternate_on=0` for its pane. The wrapper returns to `--no-alt-screen`; the still-running Codex session is not interrupted. The reason Codex did not enter tmux's alternate screen remains unknown.

## Verified 2026-09-16

The desktop build completed. `node --test tests/terminal-history.test.mjs tests/codex-shell-exit.test.mjs` passed five checks. `.venv/bin/pytest` passed the six focused terminal checks in `test_agent_instrument.py` and `test_view_landings.py`.

The live walk used a separate Electron copy under `/private/tmp` with its own user data, tmux socket, and two temporary workspaces. The real Codex CLI opened from the generated wrapper. Its `/exit` command returned to the shell; a later `printf` command ran in that same terminal; the window stayed open. A plain shell produced 120 numbered lines. The console History action opened tmux copy mode, and DevTools wheel input moved through that history before and after a workspace switch. The real Claude CLI kept xterm's alternate buffer and mouse tracking after the switch; a wheel gesture did not put its tmux pane into copy mode. Both temporary tmux sessions were disposed after the walk.
