---
type: "[[feature]]"
id: FEAT-0158
aliases: ["FEAT-0158"]
title: "A prompt dispatched from the cockpit reaches a Claude session as a submitted prompt, confirmed when its turn starts, instead of as typed keystrokes"
status: backlog
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-08
updated: 2026-10-08
source:
  - "Edwin 2026-10-08: 'Plan the implementation in a new phase.'"
  - "[[REFERENCE-FUNCTION-HOOKS-REVIEW]], 'Dispatch is a robot typing into a terminal'"
goal: "When a person dispatches a prompt to a Claude session from the cockpit, the session receives it as a submitted prompt, and the cockpit records it as delivered only once the session's turn has started."
requirements: []
tasks: []
release: ""
acceptance_exception: ""
acceptance: ""
design: ""
related:
  - "[[FEAT-0025]]"
  - "[[FEAT-0156-Claude-Sessions-Report-Through-The-Cockpit-Plugin]]"
  - "[[PHASE-040-The-Agent-Session-Is-Not-A-Terminal]]"
---

# A dispatched prompt is submitted, not typed

**Not started.** Filed at `backlog` in the planned [[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]. It needs the plugin from [[FEAT-0156-Claude-Sessions-Report-Through-The-Cockpit-Plugin]].

## Goal

Today a dispatched prompt is typed into the terminal: `desktop/src/ipc/dispatch-queue.ts:189` writes `item.prompt + '\r'` into the pseudo-terminal. So a dispatch cannot be confirmed, and the session cannot tell it from a person typing. After this feature, the cockpit's plugin inside the Claude session takes the prompt and calls `$.prompt.submit`, which waits until the session is idle and then starts a turn. The plugin tells the sidecar when that turn starts, and only then is the dispatch recorded as delivered. Codex sessions keep the typed path.

## Findings

- **Two routes reach the terminal today.** Dispatches started in the shell go through `dispatch-queue.ts` over IPC straight to the PTY. Dispatches started from the `cockpit dispatch` command are queued in the sidecar, and the renderer drains them from `GET /api/cockpit/dispatch-requests` (`renderer.ts:17598`). Both have to reach the plugin for a Claude session.
- **The sidecar queue is take-once.** `take_dispatch_requests()` (`agent_hooks.py:587`) empties the list for whoever asks first. If the plugin and the renderer both poll it, each will steal the other's requests. So requests need a session address, and each consumer takes only its own. That is a change to the sidecar contract, and the capability register needs a row for it.
- **What the plugin does.** A `$.clock.every` timer fetches requests for its session, calls `$.prompt.submit({text})`, and posts a confirmation when `turn.start` fires for that prompt. The dispatch ledger ([[FEAT-0025]]) then gets a real delivered time instead of the time keystrokes were written.
- **Codex.** `dispatch-queue.ts` keeps its Codex branch (the bracketed-paste write) and its shell-mode branch, which starts a new `claude` or `codex` command. Only the Claude REPL branch moves.
- **[[PHASE-040-The-Agent-Session-Is-Not-A-Terminal]]** (deferred) would hand session ownership to T3 Code and dispatch through it. This feature does not block that: if PHASE-040 is reopened, it replaces this route the same way it replaces the PTY one.

### Candidate tasks, minted when this feature starts

1. Address dispatch requests to a session in the sidecar, so each consumer takes only its own.
2. The plugin's poll, submit and confirm, with the ledger stamped on `turn.start`.
3. Route the shell's own Claude REPL dispatches through the sidecar to the plugin, and remove the Claude `prompt + '\r'` write.

## Open questions

1. **What happens to a request no plugin claims?** For example, a Claude session started with the kill switch on, or with an older Claude Code. Options: fall back to typing it, or hold it and show it as undelivered. Recommendation: hold and show it, because a silent fallback brings back the unconfirmable path.
2. **Can a dispatch be cancelled before its turn starts?** `$.prompt.submit` waits for the session to be idle, so there is a window. Cancelling it is new capability; it is out of scope unless Edwin wants it now.

## Links

- Phase: [[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]
- Code: `desktop/src/ipc/dispatch-queue.ts`, `src/project_os_cockpit/agent_hooks.py` (`take_dispatch_requests`), `src/project_os_cockpit/server.py` (`_serve_dispatch_requests`)
