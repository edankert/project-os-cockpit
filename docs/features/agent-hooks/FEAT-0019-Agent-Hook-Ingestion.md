---
type: "[[feature]]"
id: FEAT-0019
aliases: ["FEAT-0019"]
title: "Agent hook ingestion — auto-instrumented terminal sessions"
status: doing
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-05
updated: 2026-09-23
reviewed_by: "model:claude-opus"
review_date: 2026-07-20
review_verdict: approved
verification_waiver: "TST-0011 is a manual live-agent e2e checklist (real claude/codex launch, permission prompt, OS notification). User accepted the automated verification in lieu of the manual pass on 2026-07-20: instrumentation-pipeline smoke test (generated scripts → sidecar tracker), CDP UI checks, 409 sidecar-identity guard, 217 passing unit tests, and an independent review verdict of CLOSE for all five."
goal: "Agent lifecycle signals (busy/waiting/needs-input, current prompt, files touched, cost/context) flow into the cockpit automatically when Claude Code or Codex runs inside the embedded terminal — no voluntary cockpit-signal calls needed."
requirements: []
tasks: ["[[TASK-0114]]", "[[TASK-0115]]", "[[TASK-0116]]", "[[TASK-0117]]", "TASK-0183", "[[TASK-0633]]", "[[TASK-0634]]", "[[TASK-0636]]", "[[TASK-0637]]"]
related: ["[[FEAT-0013-Agent-State-Signal]]", "[[RISK-0004-Hook-Injection-Surface]]", "[[FEAT-0020-Agent-Activity-Surfaces]]", "[[ISS-0312]]", "[[CHG-20260916-Document-Codex-integration-gap-and-path-to-Claude-parity]]", "[[CHG-20260916-Show-Codex-session-state-and-temperature-in-cockpit]]"]
waiver_expires: 2026-10-23

---

# Agent hook ingestion

## Why

FEAT-0013's `cockpit signal` is a voluntary protocol: the LLM must remember to call it, which is why COCKPIT.md exists and why the rail dots go stale when the model forgets. Claude Code hooks can forward lifecycle events to the cockpit. The July 2026 Codex implementation used its `notify` program for turn-completion and attempted approval events; it did not install lifecycle hooks. Native Codex hooks are now documented, and the remaining integration is tracked by [[ISS-0312]].

## Goal

Launching `claude` or `codex` inside the embedded terminal instruments the session invisibly; the cockpit's existing agent-state machine, rail dots, decay thread, and OS notifications are fed by a push feed instead of voluntary CLI calls. `cockpit signal` remains as the fallback for agents in external terminals.

## Scope

1. **Ingestion endpoint.** `POST /api/agent-hook` on the sidecar: accepts Claude Code hook payloads (`session_id`, `hook_event_name`, `cwd`, `transcript_path`, event-specific fields), validates + size-caps them, and folds them into `CockpitState`. Event mapping: `UserPromptSubmit` → busy (prompt text recorded as current task), `PermissionRequest` / `Notification(permission_prompt)` → needs-input, `Notification(idle_prompt)` → waiting, `Stop` → waiting, `SessionEnd` → idle. `PreToolUse`/`PostToolUse` with `Edit|Write` matchers record the touched file. Fan out over the existing SSE channel (extend `cockpit:agent-state`, add `cockpit:agent-activity`).
2. **Claude Code injection at PTY spawn.** When `terminal.ts` spawns the workspace shell, provide per-session hook configuration (settings injection — generated settings file + env, no writes to `~/.claude`) registering `type: "http"` hooks for `SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, Notification, PermissionRequest, Stop, SubagentStart, SubagentStop, SessionEnd` pointed at the workspace's sidecar.
3. **Codex injection.** Ten per-launch native hooks forward prompt, tool, approval, completion, exit, child lifecycle and interruption events. New launchers omit the old notify callback. Normal hook trust remains required. Interrupt holds needs-input until a new user prompt or exit, including late background tool completions.
4. **Statusline forwarder.** Optional Claude Code statusline command that forwards the stdin JSON blob (cost.total_cost_usd, lines added/removed, context_window.used_percentage, rate-limit windows) to the sidecar for the FEAT-0020 meters.
5. **Precedence rules.** Hook-fed state wins over manual `cockpit signal` when both arrive for the same workspace within a session; manual signal remains authoritative when no instrumented session is live.

## Out of scope

- UI surfaces (FEAT-0020 renders what this feature ingests).
- Agents other than Claude Code and Codex (the endpoint contract is agent-agnostic; adapters for opencode/Gemini/aider can follow).
- Headless (`claude -p` / `codex exec`) orchestration.
- Parsing transcript JSONL (FEAT-0022).

## Acceptance

- Starting `claude` in the embedded terminal and submitting a prompt flips the rail dot to busy without any `cockpit signal` call; a permission prompt flips it to needs-input and raises the existing OS notification path; `Stop` flips it to waiting.
- Codex native events report busy, approval, waiting and exit; child events preserve parent state, interruption holds queued work, and queued prompts actually submit. Complete live verification remains in [[TST-0011]].
- The user's `~/.claude` and `~/.codex` configurations are not modified; running `claude` outside the cockpit terminal behaves exactly as before.
- Malformed or oversized POSTs to `/api/agent-hook` are rejected without disturbing state; payload content is never rendered as HTML.
- `cockpit signal busy` from an external terminal still works and still decays per the existing rules.

## Links

- Tasks: to be broken down (`plan/PLAN.md`)
- Prior state machine: `src/project_os_cockpit/server.py` (`CockpitState`), `desktop/src/ipc/agent-state-poller.ts`
- Spawn point: `desktop/src/ipc/terminal.ts`

## Delivery clarification — 2026-09-16

The snapshot retains this feature's July `done` status and its recorded verification waiver. That close-out covered the delivered `notify` wrapper, synthetic ingestion checks, and the Claude path; it did not prove Codex lifecycle parity. The Codex row in [[TST-0011]] was skipped, and [[TASK-0116]] now records the narrower delivered scope. [[ISS-0312]] owns the new work without reopening the completed phase.

## Codex follow-up — 2026-09-16

The cockpit wrapper now passes seven native Codex hook definitions for this launch only. Their command reads the original hook JSON on stdin and posts it to the workspace sidecar with `agent=codex`. The existing `notify` command remains a fallback. Codex's normal hook trust review still applies. The wrapper does not write to `~/.codex` or replace project hooks.

The sidecar keeps state per session before choosing one project headline. A waiting Claude session no longer masks an active Codex turn. Codex `apply_patch` file paths are read only from patch headers after the tool completes. [[TST-0011]] still needs a live Codex walk in the embedded terminal.

The next live check found why the project icon stayed stale: the active tmux shell held its old `codex` function in memory, and its Codex process received only `notify`. Newly generated hook commands also lacked shell quoting for the app state path under `Application Support`. The corrected wrapper calls a regenerated launch script, so later app rebuilds can change hook flags without restarting a shell that has loaded this wrapper. The already-running shell still needs one refresh after its Codex process exits ([[CHG-20260916-Fix-Codex-status-and-Needs-You-feed]]).

## Codex parity follow-up — 2026-09-23

The user authorized the September 23 review recommendations with “Continue as suggested.” Reopened for [[TASK-0633]], [[TASK-0634]], [[TASK-0636]] and [[TASK-0637]]. The historical reviews and waiver above cover the earlier delivered scope only. A fresh review is required when the changed feature closes. Usage research can conclude unsupported; it does not authorize new meters or session ownership.

## Verification

The historical review and waiver do not certify this extension. Implementation evidence is in [the parity verification report](../../reference/codex-parity-verification-2026-09-23.md). The full Python suite passed 2,197 tests with six skips; the desktop suite passed 224 with one skip on 2026-09-23. Focused interruption tests also pass. Commands: `.venv/bin/python -m pytest -q`; `cd desktop && npm run build && node --test tests/*.test.mjs`.

The feature remains doing because TST-0011's complete live checklist is open, including a real mixed Claude/Codex screen. Fresh independent review remains owed before feature completion. No new verification waiver was granted.

## Handoff, 2026-09-25

**Done.** Edwin re-ran [[TST-0011]] live on 2026-09-25 and all 13 rows passed. Every task under this feature and FEAT-0027 is done, ISS-0312 is fixed, TST-0010, TST-0015 and TST-0017 pass on their own commands, and PHASE-007's exit criteria are all ticked (cfb53b0).

**In flight.** One shared independent review of this feature and FEAT-0027, with two reviewers on the same packet. It covers the Codex work since the 2026-07-20 review: `1d16f08` and `9ecdeb6`, 2,646 diff lines. The packet leaves out template syncs, bundled copies and notes that the packet tool picked up by commit subject.

**Next.** Combine the two reports into a `## Review` section here and on FEAT-0027, and fix every finding about code these features changed. Then set both features `done`, record the verdict on TST-0010, TST-0011, TST-0015 and TST-0017, and close PHASE-007.

