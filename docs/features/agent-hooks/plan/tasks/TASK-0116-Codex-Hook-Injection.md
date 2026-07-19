---
type: "[[task]]"
id: TASK-0116
aliases: ["TASK-0116"]
title: "Codex CLI hooks.json + notify injection"
status: doing
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-05
updated: 2026-07-05
parent: "[[FEAT-0019-Agent-Hook-Ingestion]]"
effort: "S"
depends: ["[[TASK-0114]]"]
blocks: []
related: ["[[RISK-0004-Hook-Injection-Surface]]"]
tests: ["[[TST-0011]]"]
---

# Codex hooks.json + notify injection

## Definition of Done
- [ ] Codex sessions spawned in the cockpit PTY carry `notify` (for `agent-turn-complete` / `approval-requested`) and lifecycle hooks (`SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `PermissionRequest`, `Stop`) forwarding to the sidecar `/api/agent-hook`.
- [ ] Injection via `$CODEX_HOME`-scoped generated config under the app state dir; the user's `~/.codex` is never written.
- [ ] The one-time TUI trust prompt (non-managed hooks) is documented and surfaced honestly, never auto-approved.
- [ ] Same kill switch as TASK-0115 disables it.

## Steps
- [ ] Generate per-workspace `config.toml`/`hooks.json` fragment + notify forwarder script.
- [ ] Wire `CODEX_HOME` (or equivalent layering) into the PTY env without hiding the user's own config; verify Codex still sees user auth/session state.
- [ ] End-to-end verify with a live `codex` session; capture fixtures.

## Notes
If `CODEX_HOME` redirection would hide the user's auth, prefer the project-scoped `.codex/hooks.json` mechanism inside the workspace with an explicit opt-in, or skip transparent injection and document manual setup — never break the user's Codex login.
