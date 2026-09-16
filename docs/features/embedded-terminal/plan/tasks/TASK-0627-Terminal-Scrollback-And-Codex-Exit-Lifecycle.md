---
type: "[[task]]"
id: TASK-0627
aliases: ["TASK-0627"]
title: "Keep terminal scrolling usable and keep the cockpit open when Codex exits"
status: doing
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
related: ["[[TASK-0186]]", "[[ISS-0016]]", "[[ISS-0154]]", "[[ISS-0160]]", "[[ISS-0161]]", "[[SUR-0002]]", "[[CHG-20260916-Make-Codex-terminal-history-scrollable-through-tmux]]", "[[CHG-20260916-Keep-tmux-scrolling-after-workspace-reattachment]]"]
tests: ["tests/test_agent_instrument.py::test_codex_wrapper_preserves_terminal_scrollback", "tests/test_view_landings.py::test_the_terminal_restores_mouse_mode_only_for_an_alternate_buffer", "tests/test_view_landings.py::test_a_normal_terminal_buffer_can_scroll_past_stale_tui_mouse_mode", "tests/test_view_landings.py::test_the_console_wheel_and_history_action_reach_tmux", "tests/test_view_landings.py::test_tmux_history_survives_workspace_reattachment", "tests/test_view_landings.py::test_a_terminal_child_exit_does_not_quit_the_electron_app", "desktop/tests/terminal-history.test.mjs"]
---

# Keep terminal scrolling usable and keep the cockpit open when Codex exits

## Definition of Done

- [ ] Wheel input scrolls a normal shell's xterm history even after a TUI has run in the same pane.
- [ ] The console opens tmux history on demand, and wheel input enters that history when the inner pane uses its normal screen.
- [ ] After a project switch, the wheel still reaches tmux's full history even if the bounded terminal replay no longer contains tmux's alternate-screen entry sequence.
- [ ] Reattachment checks tmux's current mouse request before restoring xterm mouse tracking, so a shell cannot inherit a stale TUI mode.
- [ ] Claude's alternate-screen interface keeps mouse scrolling after the terminal is shown again or a workspace is switched.
- [ ] Codex keeps its notification instrumentation and inline mode. Its output can be reached through tmux history when tmux captured it, and ending it returns to the shell prompt without closing the Electron cockpit.
- [ ] Automated guards cover the wheel path and the child-exit/app-lifecycle separation.
- [ ] The rebuilt Electron terminal is walked with a plain shell, Claude, and Codex.

## Steps

- [x] Trace and repair xterm wheel handling for normal and alternate buffers, preserving Claude's behavior and launching Codex in inline mode.
- [x] Expose tmux history in the Electron console and route wheel events according to the inner pane's screen and mouse state.
- [ ] Keep PTY child exit notifications local to the terminal renderer; do not treat them as an Electron quit.
- [x] Preserve the existing Codex notification wrapper while adding `--no-alt-screen`, and add regression coverage for the wrapper.

## Notes

Sibling search found the earlier dimension, keyboard handoff, stale mouse-mode, backlog replay, and Codex scrollback issues. The new work joins their shared terminal path but does not widen [[REQ-0005]] or add a new runtime dependency.

The 2026-09-16 review found that tmux itself enters xterm's alternate screen on attach ([[ISS-0161]]). Codex's `--no-alt-screen` flag cannot make xterm use its normal buffer through that outer tmux client. The explicit History action must work even when an interactive program captures the mouse. Automatic wheel routing uses the inner tmux pane's alternate-screen state, so programs such as Claude keep their existing input behavior. tmux mouse handling remains off to preserve selection in xterm.

Edwin's live walk found that returning to a project sometimes changed the wheel from full tmux history to short or empty xterm scrollback. The renderer had required xterm's alternate-buffer state, but `term.reset()` and a capped PTY replay cannot always reconstruct that state. Wheel routing now uses the workspace's tmux backing independently of xterm's reconstructed buffer. Whether Codex should keep its prompt fixed like Claude is a separate choice about Codex's own display mode.
