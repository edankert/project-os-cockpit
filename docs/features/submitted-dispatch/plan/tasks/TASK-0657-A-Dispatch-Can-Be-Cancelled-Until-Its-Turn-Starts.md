---
type: "[[task]]"
id: TASK-0657
aliases: ["TASK-0657"]
title: "A person can cancel a dispatched prompt from the queue list until its turn starts, and is told plainly when it is too late"
status: backlog
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

- [ ] `POST /api/cockpit/deliveries/<did>/cancel` (loopback, JSON): `held` or `waiting` becomes `cancelled`; `sending` becomes `cancelling` and the answer says "pending"; `started` answers 409 with the turn's start time.
- [ ] A `started` post for a `cancelling` delivery makes it `started`, and the shell says "Too late to cancel <verb> <id>: its turn started at <time>. Press Esc in the terminal to stop it."
- [ ] A `dropped` post for a `cancelling` delivery makes it `cancelled`.
- [ ] If task 2's check (a) found that the plugin's `prompt.submit` hook sees its own submission: that hook returns `{ drop: "Cancelled from the cockpit" }` for this plugin's in-flight text when the sidecar says `cancelling`, asks within the hook's budget, and lets the prompt through when the sidecar does not answer. If check (a) found that it does not: `cancel` on a `sending` delivery answers "too late" at once, and this note says so.
- [ ] Each row that has not started has a `×` labelled "Cancel" (or "Remove" on a held or dropped row). "Clear all" cancels every row that has not started. A cancelled row disappears and the status line says "Cancelled <verb> <id>".
- [ ] The note's dispatch history lists a cancelled dispatch as cancelled, with the time.
- [ ] Tests that fail when: a cancelled delivery is still submitted after a late claim; a cancel on a started delivery stops or changes the turn; a cancel and a `started` racing leave the delivery in two states; the hook drops a prompt that was not cancelled.
- [ ] The capability register row for the routes gains cancel, and `shell.agents.strip` says what Cancel does.

## Steps

- [ ] The cancel route and the `cancelling` transitions in the sidecar.
- [ ] The plugin's `prompt.submit` hook, or the recorded reason there is none.
- [ ] The queue list's buttons, the status lines, the dispatch history.
- [ ] Tests, register.

## Notes

A started turn is not aborted, although `$.turn.abort` could: the plan's "Cancel" section says why.
