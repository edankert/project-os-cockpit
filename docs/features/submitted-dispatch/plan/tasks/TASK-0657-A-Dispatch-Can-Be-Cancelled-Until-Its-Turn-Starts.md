---
type: "[[task]]"
id: TASK-0657
aliases: ["TASK-0657"]
title: "A person can cancel a dispatched prompt from the queue list until its turn starts, and is told plainly when it is too late"
status: done
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["Edwin 2026-10-14: 'implement 2 please if we can ... would be good to know what this would look like'", "plan/PLAN.md, \"Cancel\""]
parent: "[[FEAT-0158-A-Dispatched-Prompt-Is-Submitted-Not-Typed]]"
effort: "M"
due: ""
depends: ["[[TASK-0654-The-Sidecar-Keeps-A-List-Of-Prompts-Addressed-To-A-Claude-Session]]", "[[TASK-0655-The-Plugin-Submits-A-Waiting-Prompt-And-Confirms-When-Its-Turn-Starts]]", "[[TASK-0656-The-Shell-Sends-A-Claude-Dispatch-To-The-Sidecar-And-Types-Nothing]]"]
blocks: []
related: ["[[RISK-0012-A-Local-Request-Can-Put-A-Prompt-Into-A-Claude-Session]]"]
tests: ["[[TST-0095-A-Prompt-Dispatched-To-Claude-Arrives-As-A-Submitted-Prompt-And-Can-Be-Cancelled]]"]
---

# A dispatch can be cancelled until its turn starts

Each dispatch in the queue list that has not started gets a Cancel button. Cancelling a held or waiting dispatch always works. Cancelling one the plugin is already submitting works only if the plugin's own `prompt.submit` hook can still stop it, which [[TASK-0655-The-Plugin-Submits-A-Waiting-Prompt-And-Confirms-When-Its-Turn-Starts]] finds out. A cancel that arrives after the turn started says so and leaves the turn running.

## Definition of Done

- [x] `POST /api/cockpit/deliveries/cancel` with `{did}` (loopback, JSON): `held` or `waiting` becomes `cancelled`; `sending` answers 409 at once, saying the prompt is being submitted; `started` answers 409 with the turn's start time.
- [x] A cancel refused because the turn started, or is about to, makes the shell say "Too late to cancel <verb> <id>: its turn started at <time>. Press Esc in the terminal to stop it."
- [x] Check (a) found that the plugin's `prompt.submit` hook does **not** see its own submission (TASK-0655, live run, 2026-10-14), so a `sending` delivery cannot be withdrawn: `cancel` answers "too late" at once. The `cancelling` state stays unused, and this note says so in its result.
- [x] Each row that has not started has a `×` labelled "Cancel" (or "Remove" on a held or dropped row). "Clear all" cancels every row that has not started. A cancelled row disappears and the status line says "Cancelled <verb> <id>".
- [x] The note's dispatch history lists a cancelled dispatch as cancelled, with the time.
- [x] Tests that fail when: a cancelled delivery is still submitted after a late claim; a cancel on a started delivery stops or changes the turn; a cancel and a `started` racing leave the delivery in two states; the hook drops a prompt that was not cancelled.
- [x] The capability register row for the routes gains cancel, and `shell.agents.strip` says what Cancel does.

## Steps

- [x] The cancel route and the `cancelling` transitions in the sidecar.
- [x] The plugin's `prompt.submit` hook, or the recorded reason there is none.
- [x] The queue list's buttons, the status lines, the dispatch history.
- [x] Tests, register.

## Notes

A started turn is not aborted, although `$.turn.abort` could: the plan's "Cancel" section says why.

## Result, 2026-10-14

- **The sidecar.** `cancel_delivery` in `agent_hooks.py` and `POST /api/cockpit/deliveries/cancel` with `{did}`, loopback and JSON only. `held`, `waiting` and `dropped` become `cancelled`. A cancel of a `sending` delivery answers 409, "too late: it is being submitted to Claude", and one of a `started` delivery answers 409 with its `started_at`. The turn is never touched. A cancelled delivery adds an entry to its session's dispatch history with `cancelled: true` and the time, and `dispatch_history` reports it as not live, so the re-dispatch guard does not fire on it.
- **The `cancelling` state is unused.** TASK-0655's live run found that a plugin's own `prompt.submit` hook never sees its own submission, so there is no hook that could drop a prompt once submitted. The module comment on the states says so. Accordingly, no hook drops anything, and the test this task named for "the hook drops a prompt that was not cancelled" has nothing to test.
- **The renderer.** Each delivery row in the queue list has a `×`, titled "Cancel", or "Remove" on a held or refused row. "Clear all" cancels every delivery and empties the main queue. The status line says "Cancelled <verb> <id>". When it is too late, it says "Too late to cancel <verb> <id>: its turn started at <time>. Press Esc in the terminal to stop it.", or "…: it is being submitted to Claude…". A note's provenance line reads "dispatched <verb> · claude · cancelled <time>, before it reached the session".
- **Tests.** Five in `tests/test_deliveries.py`: a cancelled delivery is never claimed; a prompt being submitted or started cannot be cancelled, and its turn is unchanged; a cancel and a start end in one state; a cancelled dispatch appears in the note's history and is not live; and the route, including that a refused cancel publishes nothing. Four breaks were tried, and each failed at least one test: a claim allowed after a cancel (3 fail), a started delivery cancellable (1 fails), a sending one cancellable (3 fail), and a cancelled entry shown as live (1 fails). The remote-peer counts move to 32 guarded routes and 35 guard calls.
- **Not checked.** The buttons and messages have not been seen in the running app; TST-0095 steps 6, 7 and 9 are the check.

