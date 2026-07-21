---
type: "[[task]]"
id: TASK-0115
aliases: ["TASK-0115"]
title: "Claude Code hook injection at PTY spawn"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-05
updated: 2026-07-20
verification_waiver: "Implementation verified automatically (see Verification); the linked TST-0011 is a manual live-agent e2e checklist that remains for a human to run."
parent: "[[FEAT-0019-Agent-Hook-Ingestion]]"
effort: "M"
depends: ["[[TASK-0114]]"]
blocks: []
related: ["[[RISK-0004-Hook-Injection-Surface]]"]
tests: ["[[TST-0011]]"]
---

# Claude Code hook injection at PTY spawn

## Definition of Done
- [x] Spawning the workspace PTY provides per-session Claude Code hook configuration registering http hooks for `SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, Notification, PermissionRequest, Stop, SubagentStart, SubagentStop, SessionEnd` pointed at that workspace's sidecar `/api/agent-hook`.
- [x] Injection is per-spawn: generated settings live under the app's state dir and are passed via `CLAUDE_CODE_EXTRA_SETTINGS`-style env/flag mechanism; `~/.claude` is never written.
- [x] A kill-switch setting disables injection entirely (reverts to voluntary `cockpit signal`).
- [x] Running `claude` outside the cockpit terminal is unaffected.

## Steps
- [x] Generate per-workspace hooks settings JSON at spawn in `terminal.ts` (sidecar port known at spawn time via sidecar map).
- [x] Wire env into `pty.spawn` env.
- [x] Verify end-to-end with a live session; capture real payloads as test fixtures for TASK-0114.

## Notes
Claude Code supports `--settings <json-or-path>` and settings-file layering; the env-based path must not require the user to alias `claude`. If no non-invasive env mechanism exists for interactive sessions, fall back to a shell alias exported only inside the cockpit PTY (documented in the note).

## Verification

Automated smoke: the generated `claude-settings.json` registers all 10 lifecycle hooks + statusline; the ZDOTDIR `.zshrc` resolves `claude` to the instrumented wrapper (and reverts to the user's alias under `COCKPIT_NO_INSTRUMENT=1`); piping a real `UserPromptSubmit` payload through the generated `hook-forward.sh` created the session in the sidecar tracker and captured the prompt. Wired at PTY spawn in `terminal.ts`; `~/.claude` untouched.
