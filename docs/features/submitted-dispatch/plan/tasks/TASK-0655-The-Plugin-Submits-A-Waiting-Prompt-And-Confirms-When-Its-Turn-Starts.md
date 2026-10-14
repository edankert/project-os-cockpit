---
type: "[[task]]"
id: TASK-0655
aliases: ["TASK-0655"]
title: "The cockpit plugin submits a waiting prompt with $.prompt.submit once the session is idle, and confirms to the sidecar when its turn starts"
status: backlog
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[FEAT-0158-A-Dispatched-Prompt-Is-Submitted-Not-Typed]], candidate task 2", "plan/PLAN.md, delivery step 2"]
parent: "[[FEAT-0158-A-Dispatched-Prompt-Is-Submitted-Not-Typed]]"
effort: "M"
due: ""
depends: ["[[TASK-0654-The-Sidecar-Keeps-A-List-Of-Prompts-Addressed-To-A-Claude-Session]]"]
blocks: ["[[TASK-0656-The-Shell-Sends-A-Claude-Dispatch-To-The-Sidecar-And-Types-Nothing]]", "[[TASK-0657-A-Dispatch-Can-Be-Cancelled-Until-Its-Turn-Starts]]"]
related: ["[[RISK-0004-Hook-Injection-Surface]]", "[[RISK-0012-A-Local-Request-Can-Put-A-Prompt-Into-A-Claude-Session]]"]
tests: []
---

# The plugin submits a waiting prompt and confirms when its turn starts

The cockpit plugin (`desktop/plugin/claude-code/hooks/register.ts`) polls the sidecar for deliveries addressed to its own session. When the session is idle it claims the oldest one, submits it as the person's own words, and tells the sidecar when the turn starts or why the prompt was refused.

## Definition of Done

- [ ] `session.start` starts a one-second `$.clock.every` poll of `GET /api/cockpit/deliveries?session=<own id>`, reading the address from `hook-env` each time. With `COCKPIT_NO_INSTRUMENT` set, or no address, nothing is polled or submitted.
- [ ] The plugin tracks whether a main-loop turn is running from `turn.start` and `turn.complete`, ignoring events that carry an `agentId`. It submits only while no main-loop turn is running, one delivery at a time, oldest first.
- [ ] It calls `claim` before submitting, and submits nothing on a 409.
- [ ] It submits with `$.prompt.submit({ text, asUser: true })`.
- [ ] It posts `started` with the `turnId` of the main-loop `turn.start` whose text matches, or of the next main-loop turn when the submit resolves with text and no match was heard. It posts `dropped` with the reason when the submit resolves with `{ drop }`.
- [ ] Every hook still passes its event on unchanged. A failed poll or post is swallowed and never slows a hook.
- [ ] Three facts checked in a real session and recorded in this note before task 4 relies on them: (a) whether the plugin's own `prompt.submit` hook sees a submission made from its timer; (b) whether `classic.UserPromptSubmit` fires for it, so the agent row shows the prompt (if not, the plugin posts that event itself on `started`); (c) whether `turn.start`'s `text` equals the submitted text with `asUser` set.
- [ ] `claude plugin test desktop/plugin/claude-code` passes cases that fail when: a prompt is submitted while a main-loop turn runs; `started` is posted before a turn starts; a 409 claim is submitted anyway; the kill switch is ignored; a subagent's `turn.start` is taken for the main loop's.
- [ ] `claude plugin validate desktop/plugin/claude-code` reports no new error.
- [ ] A live interactive run with the plugin loaded and a stand-in sidecar: one delivery submitted while idle, one while a turn ran, each confirmed. Recorded in this note.

## Steps

- [ ] The poll, the idle tracking, claim, submit and confirm in `register.ts`.
- [ ] Tests with the `claude-code/testing` kit.
- [ ] The three checks (a) to (c) and the live run.

## Notes

The declarations say `$.prompt.submit` takes no abort signal and cannot be withdrawn once called (plan, "What the mods interface gives"). Fact (a) decides whether task 4 can cancel a delivery in the `sending` stage.
