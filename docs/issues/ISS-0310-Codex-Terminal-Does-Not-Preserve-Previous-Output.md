---
type: "[[issue]]"
id: ISS-0310
aliases: ["ISS-0310"]
title: "Codex output cannot be reached through the cockpit terminal's scrollback"
status: open
owner: user:edwin
created: 2026-09-15
updated: 2026-09-16
source: ["Edwin, 2026-09-15: user report"]
severity: medium
component: desktop-terminal
phase:
parent: ""
related: ["[[FEAT-0003]]", "[[TASK-0627]]", "[[ISS-0311]]", "[[SUR-0002]]", "[[CHG-20260915-Launch-Codex-in-inline-terminal-mode-for-scrollback]]", "[[CHG-20260915-Implement-Codex-Terminal-Scrollback-Fix]]", "[[CHG-20260915-Restore-terminal-scrolling-after-workspace-reattachment]]", "[[CHG-20260915-Fix-terminal-scrollback-and-Codex-exit-lifecycle]]", "[[CHG-20260916-Make-Codex-terminal-history-scrollable-through-tmux]]", "[[CHG-20260916-Keep-tmux-scrolling-after-workspace-reattachment]]", "[[ISS-0016]]", "[[ISS-0154]]", "[[ISS-0160]]", "[[ISS-0161]]", "[[ISS-0255]]"]
tests: ["tests/test_agent_instrument.py::test_codex_wrapper_preserves_terminal_scrollback", "tests/test_view_landings.py::test_the_terminal_restores_mouse_mode_only_for_an_alternate_buffer", "tests/test_view_landings.py::test_a_normal_terminal_buffer_can_scroll_past_stale_tui_mouse_mode", "tests/test_view_landings.py::test_the_console_wheel_and_history_action_reach_tmux", "tests/test_view_landings.py::test_tmux_history_survives_workspace_reattachment", "desktop/tests/terminal-history.test.mjs"]
---

# Codex output cannot be reached through the cockpit terminal's scrollback

## Problem

The Electron cockpit does not give a person a dependable way to reach earlier Codex output by scrolling the embedded terminal. The terminal runs inside tmux, and tmux enters xterm's alternate screen when its client attaches. Codex's inline mode may help tmux retain output, but it does not put the outer xterm into its normal scrollback buffer. Claude handles scrolling inside its own interface.

> [!quote] As reported — 2026-09-15 (Edwin)
> When running codex in the cockpit, it does not scroll correctly, allowing me to see the previously  generated content.

## Repro

1. Open the Electron cockpit and show the embedded terminal.
2. Start Codex in the workspace and let it generate content.
3. Try to scroll back to earlier generated content while the Codex session remains open.
4. Repeat with Claude in the same terminal pane for comparison.
5. Compare the embedded Codex behavior with a direct Codex terminal launched with `--no-alt-screen`.

## Expected

Earlier generated content remains reachable through the terminal's scrollback while the Codex session continues running.

## Actual Before the Renderer Repair

Plain `codex` did not expose earlier generated content through the cockpit terminal's scroll path. After rebuilding with the wrapper change, Claude could also stop scrolling after workspace reattachment because `term.reset()` cleared its mouse mode.

## Evidence

- Edwin's live walk after restarting the rebuilt Electron app found full history on first opening a project, then only limited or no scrolling after leaving and returning. Claude's response region scrolls while its prompt stays in place; Codex's inline mode scrolls the terminal screen, including its prompt.
- The active Codex tmux pane still had 996 retained history lines after the report. Its inner pane was on the normal screen with no mouse tracking, so the history was present but the renderer was not reaching it.
- `attachTerminalTo` calls `term.reset()` and replays at most 256 KB of raw PTY output. Once the opening `\e[?1049h` has fallen out of that backlog, xterm can remain in its normal buffer even though the live tmux client still owns the terminal. The wheel handler incorrectly required xterm's alternate-buffer state before routing to tmux.

- `desktop/src/ipc/agent-instrument.ts:184` now adds `--no-alt-screen` to the instrumented Codex wrapper.
- `desktop/src/renderer/renderer.ts:3275` creates xterm with `scrollback: 5000`; its `ResizeObserver` and forced refit already address stale terminal geometry.
- `desktop/src/ipc/terminal.ts:35` retains only 256 KB of raw PTY output for replay after a workspace switch or app restart. This is a separate, secondary history-loss limit.
- The installed Codex CLI is version 0.154.0; its local help describes `--no-alt-screen` as inline mode that preserves terminal scrollback history.
- [[ISS-0161]] recorded the live tmux client stream starting with `\e[?1049h`, which enters xterm's alternate screen independently of Codex.
- Before this repair, the generated tmux config had a 100,000-line history limit but no mouse setting or console History action. The earlier renderer wheel interceptor handled only xterm's normal buffer, so it could not open tmux history.
- tmux's outer client remains in xterm's alternate buffer while programs inside tmux enter and leave their own alternate screens. A mouse-mode restore that checks only xterm's buffer can therefore re-enable stale tracking after an inner program exits. The attach path must check tmux's current mouse-request state before restoring it.
- Sibling search: related terminal issues [[ISS-0016]], [[ISS-0154]], [[ISS-0160]], [[ISS-0161]] and [[ISS-0255]] were reviewed. The Codex presentation mismatch and the shared reattachment regression are now tracked together because the live symptom crosses both paths.

## Implemented Fix

The generated wrappers will keep Claude's normal terminal mode and launch Codex inline:

```zsh
'claude'() { command claude --settings ... "$@"; }
'codex'() { command codex --no-alt-screen -c "notify=..." "$@"; }
```

The cockpit now offers a History action that enters tmux copy mode and routes wheel input to tmux when the inner pane uses its normal screen. On reattachment, it also checks whether that pane still requests mouse input before restoring xterm mouse tracking. The earlier claim that the inline Codex wrapper alone makes xterm's normal scrollback available through tmux was incorrect. Live Electron verification remains open.

The 2026-09-16 live walk exposed a second routing error: after reattachment, xterm can be on its normal buffer even while tmux remains the history owner. The wheel now chooses tmux from the workspace backing rather than xterm's reconstructed buffer. A post-repair live walk remains open.

## Separate Codex Display Choice

The wrapper currently forces `--no-alt-screen`, so Codex uses its inline terminal display while Claude keeps its own scrolling response area and fixed prompt. [OpenAI's Codex CLI reference](https://learn.chatgpt.com/docs/developer-commands?surface=cli) confirms that the flag disables Codex's alternate-screen mode. [OpenAI's configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference) also exposes `tui.alternate_screen` as `auto`, `always`, or `never`. It is an inference, not a verified cockpit result, that Codex's alternate-screen display may feel closer to Claude's fixed-prompt layout. Changing the wrapper would trade the current tmux-history path for Codex's own navigation and needs a separate live comparison.

## Scope and Verification

The Electron wrapper keeps Claude's normal mode and launches Codex inline. The cockpit must provide a separate route into tmux history because tmux owns the persistent terminal screen. A History action enters tmux copy mode even when a program claims mouse input. Wheel input opens that history for a normal tmux pane. An inner alternate-screen program keeps its arrow-key behavior, and direct mouse reports still reach programs that request them. tmux mouse handling stays off so the console's select-to-copy gesture continues to work.

The remaining verification is a live cockpit comparison of Codex inline scrollback, Claude alternate-screen mouse scrolling across a workspace switch, and a plain shell. It also checks that ending Codex returns to that shell without closing Electron. Source-level checks cover the wrapper and renderer paths; they do not replace the live walk.

The 256 KB PTY replay cap limits what xterm can reconstruct after a workspace switch. tmux history remains the intended source for older terminal output. The renderer checks tmux's mouse-request state on reattachment so a plain shell does not inherit a stale TUI mode. If a Codex response is absent from tmux history too, the remaining source is Codex's own transcript, which needs a separate product surface.

## Next Actions

- [ ] Confirm Claude's alternate-screen mouse scrolling and Codex's inline scrollback after a workspace switch in the Electron cockpit.
- [ ] Open tmux history from the cockpit and confirm the wheel reaches it when a program has not claimed mouse input.
- [x] Keep the generated Codex wrapper's notification option and add `--no-alt-screen`.
- [x] Add regression checks for the bounded renderer restore.
- [ ] Revisit the 256 KB replay cap as a separate terminal-history issue if workspace switching still loses older content.
