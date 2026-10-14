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

- [ ] `POST /api/cockpit/deliveries/cancel` with `{did}` (loopback, JSON): `held` or `waiting` becomes `cancelled`; `sending` answers 409 at once, saying the prompt is being submitted; `started` answers 409 with the turn's start time.
- [ ] A cancel refused because the turn started, or is about to, makes the shell say "Too late to cancel <verb> <id>: its turn started at <time>. Press Esc in the terminal to stop it."
- [ ] Check (a) found that the plugin's `prompt.submit` hook does **not** see its own submission (TASK-0655, live run, 2026-10-14), so a `sending` delivery cannot be withdrawn: `cancel` answers "too late" at once. The `cancelling` state stays unused, and this note says so in its result.
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
