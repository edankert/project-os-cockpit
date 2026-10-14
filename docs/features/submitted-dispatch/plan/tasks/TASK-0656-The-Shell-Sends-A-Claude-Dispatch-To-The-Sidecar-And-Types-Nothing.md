---
type: "[[task]]"
id: TASK-0656
aliases: ["TASK-0656"]
title: "The shell sends a dispatch for a Claude session to the sidecar instead of typing it, and the queue list shows each dispatch's state"
status: backlog
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[FEAT-0158-A-Dispatched-Prompt-Is-Submitted-Not-Typed]], candidate task 3", "plan/PLAN.md, delivery step 3"]
parent: "[[FEAT-0158-A-Dispatched-Prompt-Is-Submitted-Not-Typed]]"
effort: "M"
due: ""
depends: ["[[TASK-0654-The-Sidecar-Keeps-A-List-Of-Prompts-Addressed-To-A-Claude-Session]]", "[[TASK-0655-The-Plugin-Submits-A-Waiting-Prompt-And-Confirms-When-Its-Turn-Starts]]"]
blocks: ["[[TASK-0657-A-Dispatch-Can-Be-Cancelled-Until-Its-Turn-Starts]]"]
related: ["[[FEAT-0025]]", "[[REQ-0019-Agent-Fleet-Visibility]]"]
tests: ["[[TST-0095-A-Prompt-Dispatched-To-Claude-Arrives-As-A-Submitted-Prompt-And-Can-Be-Cancelled]]"]
---

# The shell sends a Claude dispatch to the sidecar and types nothing

`executeDispatch` in `desktop/src/ipc/dispatch-queue.ts` stops writing `prompt + '\r'` into a Claude session's terminal. It posts the dispatch to the sidecar, addressed to the live Claude session, and the window shows where each one is.

## Definition of Done

- [ ] When the workspace's live session is Claude, busy or waiting, `executeDispatch` posts the item to `POST /api/cockpit/deliveries` with that `session_id`, and writes nothing to the terminal.
- [ ] No code path in the desktop app writes a prompt into a Claude session's terminal. The `prompt + '\r'` branch is gone.
- [ ] Codex dispatches and the plain-shell branch (no live session) write exactly what they write today. Their ledger entries carry `"delivered_by": "typed"`.
- [ ] A Claude session the plugin does not claim gets a `held` delivery: nothing is typed, the chip turns amber and says `1 not delivered`, and the row says why.
- [ ] The queue chip and list show deliveries beside the main-process queue, with the row texts in the plan's state table, updated from the `cockpit:delivery` event.
- [ ] "Delivered <verb> <id>" appears in the status line when a delivery reaches `started`, not when it is posted.
- [ ] `queueDepthFor`, which the fleet view reads, counts unfinished deliveries as well.
- [ ] Node tests for the routing decision: Claude goes to the sidecar; Codex is typed; no live session runs a command; an unclaimed Claude session is held and nothing is typed.
- [ ] The capability register's `shell.agents.strip` row, and `shell.agents.codex` where it describes the Claude path, say what changed.

## Steps

- [ ] `liveSessionInfo` returns `session_id` and `plugin_claimed`.
- [ ] The routing change in `executeDispatch` and `deliver`.
- [ ] The renderer: chip, list rows, status line from the event.
- [ ] `queueDepthFor`, tests, register.

## Acceptance checks reopened

- [[TST-0011-Live-Session-Instrumentation]]: its dispatch rows for Claude now go through the plugin. Its Codex rows should pass unchanged.
