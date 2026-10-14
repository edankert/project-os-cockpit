---
type: "[[task]]"
id: TASK-0654
aliases: ["TASK-0654"]
title: "The sidecar keeps each dispatched prompt for the Claude session it is addressed to, with its state, and records it delivered when the turn starts"
status: done
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[FEAT-0158-A-Dispatched-Prompt-Is-Submitted-Not-Typed]], candidate task 1", "plan/PLAN.md, delivery step 1"]
parent: "[[FEAT-0158-A-Dispatched-Prompt-Is-Submitted-Not-Typed]]"
effort: "M"
due: ""
depends: []
blocks: ["[[TASK-0655-The-Plugin-Submits-A-Waiting-Prompt-And-Confirms-When-Its-Turn-Starts]]", "[[TASK-0656-The-Shell-Sends-A-Claude-Dispatch-To-The-Sidecar-And-Types-Nothing]]"]
related: ["[[RISK-0012-A-Local-Request-Can-Put-A-Prompt-Into-A-Claude-Session]]", "[[RISK-0005-The-Write-Surface]]", "[[REQ-0027-Every-Write-Guarded]]", "[[FEAT-0025]]"]
tests: []
---

# The sidecar keeps each dispatched prompt for its Claude session

The sidecar gains a list of deliveries: one dispatched prompt each, addressed to one Claude session, with a state from the plan's table (`held`, `waiting`, `sending`, `cancelling`, `started`, `cancelled`, `dropped`). The plugin and the shell read it and move each delivery through its states. Nothing reads or changes the existing take-once request list.

## Definition of Done

- [x] `agent_hooks.py` keeps deliveries per workspace, persisted with the sessions, at most 30 unfinished. Every change of state happens under the tracker's lock.
- [x] A new delivery starts `waiting` when its session is plugin-claimed and `held` otherwise. A `held` delivery becomes `waiting` when its session is claimed. A `waiting` one becomes `held` ("the session ended") when its session ends.
- [x] `POST /api/cockpit/deliveries`, `GET /api/cockpit/deliveries[?session=]`, and `POST /api/cockpit/deliveries/claim`, `/started` and `/dropped`, each with the delivery's `did` in the body, behave as the plan says. `claim` answers 409 for a delivery that is not `waiting`.
- [x] `started` writes the ledger entry onto that exact session, with the turn's start time, the `turn_id` and `"delivered_by": "submit"`. The note's dispatch history shows it.
- [x] Each change is published on the event stream as `cockpit:delivery`.
- [x] The session payload and `/api/cockpit/state` carry `plugin_claimed`.
- [x] Every new POST calls `_require_loopback` and reads its body through `_read_json_body`. `test_every_note_mutating_endpoint_requires_loopback` passes with the routes on its named allow-list of runtime-state routes.
- [x] pytest cases that fail when: a claim succeeds on a cancelled delivery; a delivery for session A is listed for session B; `started` stamps the ledger on the wrong session or at the claim time; a held delivery stays held after its session is claimed.
- [x] A row in `docs/reference/cockpit-capability-register.md` for the routes (`api.write.agents` and `api.read.agents` gain them).

## Steps

- [x] The delivery store and its transitions in `AgentSessionTracker`.
- [x] The routes in `server.py`, and the event.
- [x] `plugin_claimed` in `_slim`.
- [x] Tests, register row.

## Notes

The cancel route (`POST .../cancel`) and the `cancelling` handling of `started` and `dropped` belong to [[TASK-0657-A-Dispatch-Can-Be-Cancelled-Until-Its-Turn-Starts]]. This task leaves room for them in the state set, so task 4 adds a route and no new states.

## Result, 2026-10-14

- **The store.** `agent_hooks.py`: `add_delivery`, `list_deliveries` and `move_delivery` on `AgentSessionTracker`, with the states as module constants. Deliveries are saved in `.cockpit/sessions.json` beside the sessions. A sidecar that restarts marks every session ended, so it reloads every unfinished delivery as `held` ("the session ended"). At most 30 unfinished; finished ones are kept up to 30 more and then pruned.
- **Waking and holding.** The plugin's first marked post for a session (`_claim_for_plugin_locked`) moves that session's `held` ("no cockpit plugin") deliveries to `waiting`. `SessionEnd` moves its `waiting` and `sending` ones to `held` ("the session ended"). A delivery held because its session ended is not woken by a later claim. These changes come from hook events, so the tracker queues them and `/api/agent-hook` publishes them as `cockpit:delivery`.
- **The routes differ from the plan in one way.** The delivery ID is in the body, not the path: `POST /api/cockpit/deliveries/claim` with `{did}`, and the same for `started` and `dropped`. The write-guard test finds POST routes by exact path, so a path holding an ID would have escaped it. Each route calls `_require_loopback` and reads its body through `_read_json_body`, so none needed the test's runtime-only exemption. `GET /api/cockpit/deliveries` is loopback-only too, because it returns prompt text. PLAN.md and TASK-0657 now name the body form.
- **The ledger.** `started` writes the entry onto the delivery's own session, with the turn's start time the plugin sends, the `turn_id`, `delivered_by: submit` and the delivery ID. It never asks which session is live.
- **Tests.** `tests/test_deliveries.py`, 13 tests. Each of the four failures this task names was tried: a claim allowed from any state (2 tests fail), no session filter on the list (2 fail), the ledger stamped on the live session (1 fails) or at the time the delivery was added (1 fails), and a claim that does not wake a held delivery (3 fail). `test_agent_hooks.py` and `test_human_transitions.py` pass.
- **Register.** `api.read.agents` and `api.write.agents` name the routes, with a dated maintenance line.
- **The remote-peer counts.** `tests/test_remote_peer_refusal.py` counts guarded routes on purpose, so it failed until it was edited: 27 to 31 guarded POST routes, and 29 to 34 guard calls, each with a dated reason. Its sweep sends all four new POST routes from a peer the server treats as remote and gets 403. A new test there does the same for `GET /api/cockpit/deliveries`; with that route's guard removed, it fails.
- **Full suite.** `python3 -m pytest -q -p no:randomly`: the first run had those 2 failures and 2156 passed. After the edit, the remote-peer file passes 11 of 11.

