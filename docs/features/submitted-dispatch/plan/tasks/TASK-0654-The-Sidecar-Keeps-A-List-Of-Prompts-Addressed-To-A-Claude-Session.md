---
type: "[[task]]"
id: TASK-0654
aliases: ["TASK-0654"]
title: "The sidecar keeps each dispatched prompt for the Claude session it is addressed to, with its state, and records it delivered when the turn starts"
status: backlog
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

- [ ] `agent_hooks.py` keeps deliveries per workspace, persisted with the sessions, at most 30 unfinished. Every change of state happens under the tracker's lock.
- [ ] A new delivery starts `waiting` when its session is plugin-claimed and `held` otherwise. A `held` delivery becomes `waiting` when its session is claimed. A `waiting` one becomes `held` ("the session ended") when its session ends.
- [ ] `POST /api/cockpit/deliveries`, `GET /api/cockpit/deliveries[?session=]`, and `POST /api/cockpit/deliveries/<did>/claim`, `/started` and `/dropped` behave as the plan says. `claim` answers 409 for a delivery that is not `waiting`.
- [ ] `started` writes the ledger entry onto that exact session, with the turn's start time, the `turn_id` and `"delivered_by": "submit"`. The note's dispatch history shows it.
- [ ] Each change is published on the event stream as `cockpit:delivery`.
- [ ] The session payload and `/api/cockpit/state` carry `plugin_claimed`.
- [ ] Every new POST calls `_require_loopback` and reads its body through `_read_json_body`. `test_every_note_mutating_endpoint_requires_loopback` passes with the routes on its named allow-list of runtime-state routes.
- [ ] pytest cases that fail when: a claim succeeds on a cancelled delivery; a delivery for session A is listed for session B; `started` stamps the ledger on the wrong session or at the claim time; a held delivery stays held after its session is claimed.
- [ ] A row in `docs/reference/cockpit-capability-register.md` for the routes (`api.write.agents` and `api.read.agents` gain them).

## Steps

- [ ] The delivery store and its transitions in `AgentSessionTracker`.
- [ ] The routes in `server.py`, and the event.
- [ ] `plugin_claimed` in `_slim`.
- [ ] Tests, register row.

## Notes

The cancel route (`POST .../cancel`) and the `cancelling` handling of `started` and `dropped` belong to [[TASK-0657-A-Dispatch-Can-Be-Cancelled-Until-Its-Turn-Starts]]. This task leaves room for them in the state set, so task 4 adds a route and no new states.
