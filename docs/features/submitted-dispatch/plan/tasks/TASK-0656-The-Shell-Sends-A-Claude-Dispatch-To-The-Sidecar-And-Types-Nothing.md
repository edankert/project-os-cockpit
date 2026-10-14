---
type: "[[task]]"
id: TASK-0656
aliases: ["TASK-0656"]
title: "The shell sends a dispatch for a Claude session to the sidecar instead of typing it, and the queue list shows each dispatch's state"
status: done
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

- [x] When the workspace's live session is Claude, busy or waiting, `executeDispatch` posts the item to `POST /api/cockpit/deliveries` with that `session_id`, and writes nothing to the terminal.
- [x] No code path in the desktop app writes a prompt into a Claude session's terminal. The `prompt + '\r'` branch is gone.
- [x] Codex dispatches and the plain-shell branch (no live session) write exactly what they write today. Their ledger entries carry `"delivered_by": "typed"`.
- [x] A Claude session the plugin does not claim gets a `held` delivery: nothing is typed, the chip turns amber and says `1 not delivered`, and the row says why.
- [x] The queue chip and list show deliveries beside the main-process queue, with the row texts in the plan's state table, updated from the `cockpit:delivery` event.
- [x] "Delivered <verb> <id>" appears in the status line when a delivery reaches `started`, not when it is posted.
- [x] `queueDepthFor`, which the fleet view reads, counts unfinished deliveries as well.
- [x] Node tests for the routing decision: Claude goes to the sidecar; Codex is typed; no live session runs a command; an unclaimed Claude session is held and nothing is typed.
- [x] The capability register's `shell.agents.strip` row, and `shell.agents.codex` where it describes the Claude path, say what changed.

## Steps

- [x] `liveSessionInfo` returns `session_id` and `plugin_claimed`.
- [x] The routing change in `executeDispatch` and `deliver`.
- [x] The renderer: chip, list rows, status line from the event.
- [x] `queueDepthFor`, tests, register.

## Acceptance checks reopened

- [[TST-0011-Live-Session-Instrumentation]]: its dispatch rows for Claude now go through the plugin. Its Codex rows should pass unchanged.

## Result, 2026-10-14

- **Routing.** `desktop/src/ipc/dispatch-queue.ts` decides the route in one exported function, `routeFor`. A live Claude session gets `submit`, whatever its state: the item goes to `POST /api/cockpit/deliveries` with the session's ID, because the plugin waits for idle itself. A busy Codex session is queued, a waiting Codex session is pasted as before, and a workspace with no live session runs `<agent> '<prompt>'` as before. A live session of any other agent is held in the queue rather than typed into. The `prompt + '\r'` write is gone. If the sidecar refuses the delivery or does not answer, the item goes back to the front of the queue, and the next state change tries again; it is never typed instead.
- **Ledger.** A typed dispatch's entry carries `delivered_by: typed` (`record_dispatch` accepts it). A submitted one is stamped by the sidecar at its turn's start (TASK-0654).
- **The renderer.** `renderer.ts`: `activeDeliveries` is read from `GET /api/cockpit/deliveries` when a workspace opens and kept current by the `cockpit:delivery` event. The queue list shows each open delivery with its state's text from the plan's table. The chip counts them with the main queue, turns amber (`is-undelivered`) and says `N not delivered` when one is held or dropped. "Delivered <verb> <id>: its turn started" appears on `started`; "Sent <verb> <id> to Claude: it starts when Claude is idle" when the shell hands it over. Cancel buttons on these rows are TASK-0657.
- **Fleet depth.** Done in `agents-fleet.ts` rather than in `queueDepthFor`: the fleet row already fetches `/api/cockpit/state`, which now carries `deliveries_open`, and adds it to the main queue's depth. `queueDepthFor` stays the main process's own count.
- **Tests.** `desktop/tests/submitted-dispatch.test.mjs`, 6 tests. They run the built module against a real HTTP server standing in for the sidecar and record every terminal write. They cover: a live Claude session, busy or not, gets a delivery and nothing is typed; an unclaimed one is held and nothing is typed; Codex is pasted and its ledger entry is marked typed; no live session runs the command; a refused delivery stays queued and untyped; and the routing table. Four breaks were tried on the built module, and each failed at least one test: no Claude route, any live REPL typed, typed entries unmarked, and a refused delivery typed instead. `tests/test_deliveries.py` gains two tests for `delivered_by` and `deliveries_open`. Desktop suite: 202 passed. `python3 -m pytest -q -p no:randomly`: 2161 passed, 11 skipped. `npx tsc --noEmit`: clean.
- **Not checked.** The renderer change has not been seen in the running app; TST-0095 is the check. The register's `shell.agents.codex` row needed no change, because it does not describe the Claude path.

