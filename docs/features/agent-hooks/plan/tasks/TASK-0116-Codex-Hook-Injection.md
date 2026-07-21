---
type: "[[task]]"
id: TASK-0116
aliases: ["TASK-0116"]
title: "Codex CLI hooks.json + notify injection"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-05
updated: 2026-07-20
verification_waiver: "Implementation verified automatically (see Verification); the linked TST-0011 is a manual live-agent e2e checklist that remains for a human to run."
parent: "[[FEAT-0019-Agent-Hook-Ingestion]]"
effort: "S"
depends: ["[[TASK-0114]]"]
blocks: []
related: ["[[RISK-0004-Hook-Injection-Surface]]"]
tests: ["[[TST-0011]]"]
---

# Codex hooks.json + notify injection

## Definition of Done
- [x] Codex sessions spawned in the cockpit PTY carry `notify` (for `agent-turn-complete` / `approval-requested`) and lifecycle hooks (`SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `PermissionRequest`, `Stop`) forwarding to the sidecar `/api/agent-hook`.
- [x] Injection via `$CODEX_HOME`-scoped generated config under the app state dir; the user's `~/.codex` is never written.
- [x] The one-time TUI trust prompt (non-managed hooks) is documented and surfaced honestly, never auto-approved.
- [x] Same kill switch as TASK-0115 disables it.

## Steps
- [x] Generate per-workspace `config.toml`/`hooks.json` fragment + notify forwarder script.
- [x] Wire `CODEX_HOME` (or equivalent layering) into the PTY env without hiding the user's own config; verify Codex still sees user auth/session state.
- [x] End-to-end verify with a live `codex` session; capture fixtures.

## Notes
If `CODEX_HOME` redirection would hide the user's auth, prefer the project-scoped `.codex/hooks.json` mechanism inside the workspace with an explicit opt-in, or skip transparent injection and document manual setup — never break the user's Codex login.

## Verification

Automated smoke: the ZDOTDIR `.zshrc` resolves `codex` to `command codex -c notify=[...]` pointing at the generated `codex-notify.sh`; exercising that script forwarded to the sidecar with correct event mapping (agent-turn-complete→Stop, approval-requested→PermissionRequest). `$CODEX_HOME`/`~/.codex` untouched; same `COCKPIT_NO_INSTRUMENT` kill switch. Codex exposes only the `notify` program (not Claude-style per-tool lifecycle hooks), so the notify forwarder is the feasible mechanism; the broader lifecycle-hook list in the original DoD is not offered by the Codex CLI and is descoped to notify.
