---
type: "[[feature]]"
id: FEAT-0019
aliases: ["FEAT-0019"]
title: "Agent hook ingestion — auto-instrumented terminal sessions"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-05
updated: 2026-07-20
reviewed_by: "model:claude-opus"
review_date: 2026-07-20
review_verdict: approved
verification_waiver: "TST-0011 is a manual live-agent e2e checklist (real claude/codex launch, permission prompt, OS notification). User accepted the automated verification in lieu of the manual pass on 2026-07-20: instrumentation-pipeline smoke test (generated scripts → sidecar tracker), CDP UI checks, 409 sidecar-identity guard, 217 passing unit tests, and an independent review verdict of CLOSE for all five."
goal: "Agent lifecycle signals (busy/waiting/needs-input, current prompt, files touched, cost/context) flow into the cockpit automatically when Claude Code or Codex runs inside the embedded terminal — no voluntary cockpit-signal calls needed."
requirements: []
tests: ["[[TST-0010]]", "[[TST-0011]]"]
tasks: ["[[TASK-0114]]", "[[TASK-0115]]", "[[TASK-0116]]", "[[TASK-0117]]"]
related: ["[[FEAT-0013-Agent-State-Signal]]", "[[RISK-0004-Hook-Injection-Surface]]", "[[FEAT-0020-Agent-Activity-Surfaces]]"]
---

# Agent hook ingestion

## Why

FEAT-0013's `cockpit signal` is a voluntary protocol: the LLM must remember to call it, which is why COCKPIT.md exists and why the rail dots go stale when the model forgets. Claude Code and Codex CLI expose the same signals automatically: Claude Code hooks can POST structured JSON to a localhost URL on every lifecycle event, and Codex supports a Claude-compatible `hooks.json` plus a `notify` program for `agent-turn-complete` / `approval-requested`. The desktop shell spawns the PTY, so it can inject this instrumentation per-session without touching the user's own configuration.

## Goal

Launching `claude` or `codex` inside the embedded terminal instruments the session invisibly; the cockpit's existing agent-state machine, rail dots, decay thread, and OS notifications are fed by a push feed instead of voluntary CLI calls. `cockpit signal` remains as the fallback for agents in external terminals.

## Scope

1. **Ingestion endpoint.** `POST /api/agent-hook` on the sidecar: accepts Claude Code hook payloads (`session_id`, `hook_event_name`, `cwd`, `transcript_path`, event-specific fields), validates + size-caps them, and folds them into `CockpitState`. Event mapping: `UserPromptSubmit` → busy (prompt text recorded as current task), `PermissionRequest` / `Notification(permission_prompt|idle_prompt)` → needs-input, `Stop` → waiting, `SessionEnd` → idle. `PreToolUse`/`PostToolUse` with `Edit|Write` matchers record the touched file. Fan out over the existing SSE channel (extend `cockpit:agent-state`, add `cockpit:agent-activity`).
2. **Claude Code injection at PTY spawn.** When `terminal.ts` spawns the workspace shell, provide per-session hook configuration (settings injection — generated settings file + env, no writes to `~/.claude`) registering `type: "http"` hooks for `SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, Notification, PermissionRequest, Stop, SubagentStart, SubagentStop, SessionEnd` pointed at the workspace's sidecar.
3. **Codex injection.** Equivalent `hooks.json` (`SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `PermissionRequest`, `Stop`) plus `notify` program for `agent-turn-complete` / `approval-requested`. Handle the one-time TUI trust prompt honestly (document it; do not auto-trust).
4. **Statusline forwarder.** Optional Claude Code statusline command that forwards the stdin JSON blob (cost.total_cost_usd, lines added/removed, context_window.used_percentage, rate-limit windows) to the sidecar for the FEAT-0020 meters.
5. **Precedence rules.** Hook-fed state wins over manual `cockpit signal` when both arrive for the same workspace within a session; manual signal remains authoritative when no instrumented session is live.

## Out of scope

- UI surfaces (FEAT-0020 renders what this feature ingests).
- Agents other than Claude Code and Codex (the endpoint contract is agent-agnostic; adapters for opencode/Gemini/aider can follow).
- Headless (`claude -p` / `codex exec`) orchestration.
- Parsing transcript JSONL (FEAT-0022).

## Acceptance

- Starting `claude` in the embedded terminal and submitting a prompt flips the rail dot to busy without any `cockpit signal` call; a permission prompt flips it to needs-input and raises the existing OS notification path; `Stop` flips it to waiting.
- The same works for `codex` via `notify`/hooks.json (modulo the documented one-time trust prompt).
- The user's `~/.claude` and `~/.codex` configurations are not modified; running `claude` outside the cockpit terminal behaves exactly as before.
- Malformed or oversized POSTs to `/api/agent-hook` are rejected without disturbing state; payload content is never rendered as HTML.
- `cockpit signal busy` from an external terminal still works and still decays per the existing rules.

## Links

- Tasks: to be broken down (`plan/PLAN.md`)
- Prior state machine: `src/project_os_cockpit/server.py` (`CockpitState`), `desktop/src/ipc/agent-state-poller.ts`
- Spawn point: `desktop/src/ipc/terminal.ts`
