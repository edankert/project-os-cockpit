---
type: "[[task]]"
id: TASK-0116
aliases: ["TASK-0116"]
title: "Codex CLI notify injection"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-05
updated: 2026-09-25
parent: "[[FEAT-0019-Agent-Hook-Ingestion]]"
effort: "S"
depends: ["[[TASK-0114]]"]
blocks: []
related: ["[[RISK-0004-Hook-Injection-Surface]]", "[[ISS-0312]]", "[[CHG-20260916-Document-Codex-integration-gap-and-path-to-Claude-parity]]", "[[CHG-20260916-Show-Codex-session-state-and-temperature-in-cockpit]]"]
tests: ["[[TST-0011]]"]

---

# Codex CLI notify injection

## Delivered scope
- [x] Codex sessions started in the cockpit's zsh PTY receive a `notify` callback that forwards turn-complete payloads and attempts to map approval-requested payloads to `/api/agent-hook`.
- [x] The callback script lives in the app state directory, and the wrapper passes its path through Codex's `-c notify=...` option. The implementation does not redirect `$CODEX_HOME` or write `~/.codex`.
- [x] The `COCKPIT_NO_INSTRUMENT` kill switch disables the wrapper.

## Original plan not delivered
- [ ] Generate and load native Codex lifecycle hooks for `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `PermissionRequest`, `Stop`, and `SessionEnd`.
- [ ] Verify Codex's hook trust review and user authentication with the chosen installation path.
- [ ] Complete the live Codex row in [[TST-0011]] or its successor, including approval and session exit.

These items are rehomed to [[ISS-0312]]. This task remains `done` for the narrower July 2026 `notify` delivery; the checked lifecycle-hook, `$CODEX_HOME`, trust-prompt, and live-verification claims in its earlier record were incorrect.

## Notes
Do not redirect `CODEX_HOME` if that hides user authentication or session state. A project `.codex/hooks.json` requires trust review. An external user-level installation requires explicit opt-in under [[RISK-0004]]. [[ISS-0312]] records the installation choice to settle before implementation.

## Verification

The automated smoke checks the ZDOTDIR `.zshrc` wrapper and sends synthetic `agent-turn-complete` and `approval-requested` payloads through `codex-notify.sh` to the sidecar. It does not prove that the installed Codex CLI emits both payloads in a live session. The Codex row in [[TST-0011]] was skipped. OpenAI's current [Hooks documentation](https://learn.chatgpt.com/docs/hooks) describes native lifecycle hooks, so the earlier statement that Codex exposes only `notify` is obsolete.

## Follow-up delivery — 2026-09-16

[[ISS-0312]] now supplies native per-launch Codex hooks for prompt, tool, approval, stop, and session boundaries. This does not change the July scope or its recorded verification waiver. The new wrapper and sidecar paths have automated checks; the real CLI and UI walkthrough in [[TST-0011]] is still outstanding.

## Waiver retired, 2026-09-25

This note was closed on 2026-07-20 under a waiver of [[TST-0011]], the manual live-agent checklist. Edwin ran that checklist live on 2026-09-25 and all 13 rows passed, so the waiver is retired and the gate is met by the test itself.
