---
type: "[[issue]]"
id: ISS-0310
aliases: ["ISS-0310"]
title: "Codex output cannot be reached through the cockpit terminal's scrollback"
status: fixed
owner: user:edwin
created: 2026-09-15
updated: 2026-09-16
source: ["Edwin, 2026-09-15: user report"]
severity: medium
component: desktop-terminal
phase: "[[PHASE-004-Embedded-Terminal]]"
parent: ""
related: ["[[FEAT-0003]]", "[[TASK-0627]]", "[[ISS-0311]]", "[[SUR-0002]]", "[[CHG-20260915-Launch-Codex-in-inline-terminal-mode-for-scrollback]]", "[[CHG-20260915-Implement-Codex-Terminal-Scrollback-Fix]]", "[[CHG-20260915-Restore-terminal-scrolling-after-workspace-reattachment]]", "[[CHG-20260915-Fix-terminal-scrollback-and-Codex-exit-lifecycle]]", "[[CHG-20260916-Make-Codex-terminal-history-scrollable-through-tmux]]", "[[CHG-20260916-Keep-tmux-scrolling-after-workspace-reattachment]]", "[[CHG-20260916-Trial-Codex-alternate-screen-display-in-the-Electron-console]]", "[[CHG-20260916-Revert-ineffective-Codex-alternate-screen-trial]]", "[[CHG-20260916-Finish-PHASE-004-terminal-scrollback-and-Codex-exit]]", "[[ISS-0016]]", "[[ISS-0154]]", "[[ISS-0160]]", "[[ISS-0161]]", "[[ISS-0255]]"]
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

- The committed baseline at `17ca5b3` adds `--no-alt-screen` to the instrumented Codex wrapper. The trial briefly replaced it with `tui.alternate_screen="always"`, then the wrapper returned to the baseline.
- Edwin's 2026-09-16 comparison found no visible scrolling change. The active Codex process in the cockpit workspace had `-c tui.alternate_screen="always"` in its arguments, but tmux reported `alternate_on=0` and `mouse_any_flag=0` for that pane. The setting reached Codex; the expected alternate-screen transition did not occur in this live session. The cause inside Codex is unproven. [Official OpenAI documentation](https://learn.chatgpt.com/docs/config-file/config-reference) describes `always` as an alternate-screen setting; a [similar open Codex issue](https://github.com/openai/codex/issues/24552) reports it not taking effect in a tmux-like terminal on an older CLI version.
- The same live tmux pane retained 1,139 history lines. Its previous output is still present in tmux even though the alternate-screen trial did not change Codex's presentation.
- `desktop/src/renderer/renderer.ts:3275` creates xterm with `scrollback: 5000`; its `ResizeObserver` and forced refit already address stale terminal geometry.
- `desktop/src/ipc/terminal.ts:35` retains only 256 KB of raw PTY output for replay after a workspace switch or app restart. This is a separate, secondary history-loss limit.
- The installed Codex CLI is version 0.154.0; its local help describes `--no-alt-screen` as inline mode that preserves terminal scrollback history.
- [[ISS-0161]] recorded the live tmux client stream starting with `\e[?1049h`, which enters xterm's alternate screen independently of Codex.
- Before this repair, the generated tmux config had a 100,000-line history limit but no mouse setting or console History action. The earlier renderer wheel interceptor handled only xterm's normal buffer, so it could not open tmux history.
- tmux's outer client remains in xterm's alternate buffer while programs inside tmux enter and leave their own alternate screens. A mouse-mode restore that checks only xterm's buffer can therefore re-enable stale tracking after an inner program exits. The attach path must check tmux's current mouse-request state before restoring it.
- Sibling search: related terminal issues [[ISS-0016]], [[ISS-0154]], [[ISS-0160]], [[ISS-0161]] and [[ISS-0255]] were reviewed. The Codex presentation mismatch and the shared reattachment regression are now tracked together because the live symptom crosses both paths.

## Implemented Fix

The committed baseline keeps Claude's normal terminal mode and launches Codex inline:

```zsh
'claude'() { command claude --settings ... "$@"; }
'codex'() { command codex --no-alt-screen -c "notify=..." "$@"; }
```

The cockpit now offers a History action that enters tmux copy mode and routes wheel input to tmux when the inner pane uses its normal screen. On reattachment, it also checks whether that pane still requests mouse input before restoring xterm mouse tracking. The earlier claim that the inline Codex wrapper alone makes xterm's normal scrollback available through tmux was incorrect. The 2026-09-16 isolated Electron walk verified the route with real wheel input.

The earlier 2026-09-16 live walk exposed a second routing error: after reattachment, xterm can be on its normal buffer even while tmux remains the history owner. The wheel now chooses tmux from the workspace backing rather than xterm's reconstructed buffer. A later isolated Electron walk confirmed scrolling after a workspace switch.

## Separate Codex Display Choice

The cockpit keeps the committed `--no-alt-screen` baseline, so Codex uses its inline terminal display while Claude keeps its own scrolling response area and fixed prompt. [OpenAI's Codex CLI reference](https://learn.chatgpt.com/docs/developer-commands?surface=cli) confirms that the flag disables Codex's alternate-screen mode. [OpenAI's configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference) exposes `tui.alternate_screen` as `auto`, `always`, or `never`. The alternate-screen trial reached the running Codex process but did not change the observed scrolling behavior, so it was reversed ([[CHG-20260916-Revert-ineffective-Codex-alternate-screen-trial]]). Already-running Codex processes and shells keep their loaded commands until they exit or restart.

## Scope and Verification

The committed Electron wrapper keeps Claude's normal mode and launches Codex inline. The cockpit must provide a separate route into tmux history because tmux owns the persistent terminal screen. A History action enters tmux copy mode even when a program claims mouse input. Wheel input opens that history for a normal tmux pane. An inner alternate-screen program keeps its arrow-key behavior, and direct mouse reports still reach programs that request them. tmux mouse handling stays off so the console's select-to-copy gesture continues to work.

The 2026-09-16 live walk used an isolated rebuilt Electron copy and two temporary workspaces. A plain shell produced 120 numbered lines. The console History action opened tmux copy mode, and a real DevTools wheel gesture moved the first visible line from `HISTORY_LINE_105` to `HISTORY_LINE_090`. After switching workspaces and returning, another gesture moved it from `HISTORY_LINE_096` to `HISTORY_LINE_081`. Claude Code 2.1.271 kept its alternate screen and mouse tracking after the switch; the wheel did not enter tmux copy mode. Codex CLI 0.154.0 exited back to a working shell prompt without closing Electron ([[TASK-0627]]).

The 256 KB PTY replay cap limits what xterm can reconstruct after a workspace switch. tmux history remains the intended source for older terminal output. The renderer checks tmux's mouse-request state on reattachment so a plain shell does not inherit a stale TUI mode. If a Codex response is absent from tmux history too, the remaining source is Codex's own transcript, which needs a separate product surface.

## Next Actions

- [x] Confirm Claude's alternate-screen mouse path and Codex's tmux scrollback after a workspace switch in the Electron cockpit.
- [x] Compare an alternate-screen Codex session with the committed inline-mode baseline. Edwin saw no scrolling change, and the live tmux pane remained on its normal screen.
- [x] Open tmux history from the cockpit and confirm the wheel reaches it when a program has not claimed mouse input.
- [x] Keep the generated Codex wrapper's notification option and add `--no-alt-screen`.
- [x] Add regression checks for the bounded renderer restore.
- [~] The 256 KB replay cap did not block the tmux history walk. Revisit it under a separate issue if a later observation shows missing output in tmux itself.
