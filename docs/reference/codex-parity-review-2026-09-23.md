---
type: "[[reference]]"
id: REFERENCE-CODEX-PARITY-20260923
title: "Codex integration review and the next steps toward Claude Code parity"
status: active
owner: user:edwin
created: 2026-09-23
updated: 2026-09-23
scope: "project"
source:
  - "User request, 2026-09-23"
  - "https://learn.chatgpt.com/docs/hooks"
  - "https://learn.chatgpt.com/docs/app-server"
related:
  - "[[ISS-0312]]"
  - "[[TST-0011]]"
  - "[[FEAT-0027]]"
  - "[[PHASE-040]]"
  - tools/adapters/codex/ADAPTER.md
---

# Codex integration review and next steps

Codex already has the native project-os adapter and most embedded-terminal instrumentation. The next step is to verify that complete workflow, then close the remaining telemetry and external-terminal gaps. Rebuilding the adapter or adopting a new session host is unnecessary for that first step.

## Request and scope

> Review the current codex integration efforts and suggest what to do next to create claude code parity.

This review enables Edwin to choose the next implementation slice from the remaining gaps. It records recommendations, not an approved multi-feature scaffold.

Reviewed `main` at `abd73db`, with a clean working tree at startup. The installed CLI reports `codex-cli 0.156.1`. Focus remains on `TASK-0631` / `FEAT-0151`; this review does not advance that guided-walk work. No application code, user configuration, session state, or lifecycle verdict was changed.

## What is delivered

| Area | Current evidence | Parity assessment |
| --- | --- | --- |
| Repository workflow | Commit `b546625` added `.codex/hooks.json`, two `.codex/agents/` profiles, and 27 `.agents/skills/` playbooks. The generator reports all 67 adapter artifacts current. | Native integration is present. The adapter guide's claim that these files remain unsynced is obsolete. |
| Project-os enforcement | [Codex dispatcher](../../tools/adapters/codex/hooks/dispatch.py) implements the first eight shared hook contracts. Twelve adapter fixture tests pass. | Core checks exist. Fixtures do not establish that every gate behaves identically in a real Codex session. |
| Embedded sessions | [Instrumentation](../../desktop/src/ipc/agent-instrument.ts) injects seven Codex lifecycle hooks, keeps `notify` as a fallback, and uses a regenerated launcher. | Prompt, tools, approval, stop, and exit reporting are implemented. |
| Cockpit state and activity | [Ingestion](../../src/project_os_cockpit/agent_hooks.py) tracks sessions separately, suppresses duplicate fallback notifications, and extracts Codex patch paths. Renderer tests cover a busy Codex session beside a waiting Claude session. | Much of the original state and Needs You gap is repaired. The complete live walk remains owed. |
| Terminal behavior | The shell-exit and tmux History tests pass. | The earlier terminal defects have implemented fixes; do not reopen them merely because the wider parity issue remains open. |
| Account allowance | [Codex usage reader](../../desktop/src/ipc/codex-usage.ts) uses App Server to read the general weekly account allowance. | Delivered account quota, distinct from session context, tokens, or cost. |
| External sessions | [Settings integration](../../desktop/src/ipc/app-settings.ts) installs only into Claude's user settings. | Codex has no equivalent cockpit opt-in. Project workflow hooks do not provide this telemetry. |
| Session meters and cache | Codex has no counterpart to the injected Claude statusline. Cache lookup is explicitly restricted to Claude in `agent_hooks.py`. | Context and session usage remain missing. `cache unknown` is an accurate limitation. |

## Recommended order

### 1. Finish the existing integration's live acceptance check

Use [[ISS-0312]] and the Codex procedure in [[TST-0011]]. Record one complete run against the rebuilt Electron app: trust review, prompt, working state, approval, completed turn, another prompt, and exit to the same shell. Include a waiting Claude session in the same workspace.

Then exercise queued prompts while switching workspaces, app reattachment, an older tmux shell, History, and the instrumentation kill switch. Compare visible state with sidecar events. The September 16 evidence includes several successful screen checks, but explicitly leaves the complete sequence open.

The acceptance result should certify reliable state and dispatch. Keep session usage and cache estimation separate so an unavailable cache metric does not prevent closing a verified lifecycle repair.

### 2. Complete the small lifecycle gaps

Codex's wrapper forwards seven events; Claude's forwards ten. The missing subagent events are actionable: current [OpenAI hook documentation](https://learn.chatgpt.com/docs/hooks) describes `SubagentStart` and `SubagentStop`, and the sidecar already handles those names. Verify their payloads on the installed CLI, then forward them with tests that preserve the parent session's state.

The same documentation describes `Interrupt`, which neither the Codex event list nor the sidecar currently handles. Check cancellation explicitly before choosing its state mapping. A cancelled turn must not strand the project at “working” or release queued work prematurely. Documented availability is not evidence that this version has passed that test.

### 3. Add external-terminal Codex instrumentation

Extend the existing external-session feature with a separate Codex opt-in. Install and remove only cockpit-owned hook entries, retain the normal hook trust review, and preserve existing user configuration and login state. Test enable, disable, sidecar absence, restart, and simultaneous embedded/external sessions. Confirm that overlapping user and launch hooks do not duplicate activity or dispatch.

This is the clearest missing everyday capability relative to the cockpit's Claude integration. It belongs in cockpit settings and telemetry, while shared project-os adapter changes belong upstream.

### 4. Establish a supported source for session usage

Run a bounded investigation before building meters. [App Server](https://learn.chatgpt.com/docs/app-server) documents `thread/tokenUsage/updated` for active threads and `thread/read` for stored threads. Reading a thread does not subscribe to its events. The existing short-lived account-quota process therefore does not establish access to the independently running terminal session's live usage.

Prove how the cockpit identifies and observes that exact thread without accidentally resuming or taking ownership of it. Prefer supported protocol data; hook documentation says transcript format is not stable. Deliver model, measured token usage, and context occupancy only where the source supports them. Keep account allowance, measured usage, and any dollar estimate separately labelled.

Do not copy Claude's one-hour cache assumption. A cached-token count does not prove when the next turn's cache expires or what that turn will cost. Keep `cache unknown` until a defensible source exists.

### 5. Reconcile the adapter guidance and remaining enforcement differences

Update [the Codex guide](../../tools/adapters/codex/ADAPTER.md) and the historical checklist in [[ISS-0312]] so nobody schedules the already-delivered adapter sync again. Keep the historical evidence, but label it as historical.

[HC-010](../../tools/instructions/HOOKS.md) records another real difference: Claude enforces reviewer tool-call budgets, while Codex relies on the skill instruction. Current hook documentation names subagents on start/stop events but does not establish that every tool event carries that identity. Verify correlation before attempting the same enforcement. Core live gate tests should also cover documentation-first refusal, an invalid completion, and Stop validation while telemetry is enabled.

The startup hint in this review emitted an empty status for `TASK-0631`. Its note says `doing`, but the task is absent from snapshot item membership; the dispatcher only searches those items. This is a shared state-curation problem to reconcile before using that hint as evidence of correct lifecycle routing.

## Keep the larger session-host decision separate

[[PHASE-040]] proposes replacing tmux with a dedicated agent-session service. Its note has status `planned`, while [[ISS-0312]] and the snapshot narrative record Edwin's deferral. This review does not reopen it. If the usage investigation requires moving session ownership, return to that architectural decision with evidence instead of introducing another owner inside a telemetry change.

## Verification performed

All checks below passed on 2026-09-23:

- `bash tools/scripts/test-codex-adapter.sh`: 12 adapter tests.
- `python3 tools/scripts/generate-adapters.py --check`: all 67 generated artifacts current.
- `.venv/bin/python -m pytest -q tests/test_agent_hooks.py tests/test_agent_state.py tests/test_dispatch_ledger.py tests/test_external_hook.py`: 43 tests.
- `cd desktop && npm run build`: TypeScript and asset build passed before running the renderer tests.
- From `desktop/`, `node --test tests/attention-mixed-session.test.mjs tests/attention-dismissal.test.mjs tests/cache-temperature.test.mjs tests/codex-shell-exit.test.mjs tests/codex-usage.test.mjs tests/terminal-history.test.mjs`: 38 tests.

These are focused automated checks, not a live Electron acceptance run. No new runtime risk is introduced by this reference note. Revisit it after the live walk or a Codex version change.

## Implementation follow-up

The user subsequently authorized this sequence. See [implementation and verification](codex-parity-verification-2026-09-23.md) for the delivered changes and remaining checks; the review above records the pre-implementation baseline.
