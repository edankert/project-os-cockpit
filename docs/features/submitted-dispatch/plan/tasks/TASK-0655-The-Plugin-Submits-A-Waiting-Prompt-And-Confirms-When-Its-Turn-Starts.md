---
type: "[[task]]"
id: TASK-0655
aliases: ["TASK-0655"]
title: "The cockpit plugin submits a waiting prompt with $.prompt.submit once the session is idle, and confirms to the sidecar when its turn starts"
status: done
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

- [x] `session.start` starts a one-second `$.clock.every` poll of `GET /api/cockpit/deliveries?session=<own id>`, reading the address from `hook-env` each time. With `COCKPIT_NO_INSTRUMENT` set, or no address, nothing is polled or submitted.
- [x] The plugin tracks whether a main-loop turn is running from `turn.start` and `turn.complete`, ignoring events that carry an `agentId`. It submits only while no main-loop turn is running, one delivery at a time, oldest first.
- [x] It calls `claim` before submitting, and submits nothing on a 409.
- [x] It submits with `$.prompt.submit({ text, asUser: true })`.
- [x] It posts `started` with the `turnId` of the main-loop `turn.start` whose text matches, or of the next main-loop turn when the submit resolves with text and no match was heard. It posts `dropped` with the reason when the submit resolves with `{ drop }`.
- [x] Every hook still passes its event on unchanged. A failed poll or post is swallowed and never slows a hook.
- [x] Three facts checked in a real session and recorded in this note before task 4 relies on them: (a) whether the plugin's own `prompt.submit` hook sees a submission made from its timer; (b) whether `classic.UserPromptSubmit` fires for it, so the agent row shows the prompt (if not, the plugin posts that event itself on `started`); (c) whether `turn.start`'s `text` equals the submitted text with `asUser` set.
- [x] `claude plugin test desktop/plugin/claude-code` passes cases that fail when: a prompt is submitted while a main-loop turn runs; `started` is posted before a turn starts; a 409 claim is submitted anyway; the kill switch is ignored; a subagent's `turn.start` is taken for the main loop's.
- [x] `claude plugin validate desktop/plugin/claude-code` reports no new error.
- [x] A live interactive run with the plugin loaded and a stand-in sidecar: one delivery submitted while idle, one while a turn ran, each confirmed. Recorded in this note.

## Steps

- [x] The poll, the idle tracking, claim, submit and confirm in `register.ts`.
- [x] Tests with the `claude-code/testing` kit.
- [x] The three checks (a) to (c) and the live run.

## Notes

The declarations say `$.prompt.submit` takes no abort signal and cannot be withdrawn once called (plan, "What the mods interface gives"). Fact (a) decides whether task 4 can cancel a delivery in the `sending` stage.

## Result, 2026-10-14

- **The code.** `desktop/plugin/claude-code/hooks/register.ts`. `session.start` starts a one-second `$.clock.every`; the end of a main-loop turn starts it too, for a plugin reloaded mid-session. Each tick, `deliverOne` asks `GET /api/cockpit/deliveries?session=<own id>` and takes the oldest `waiting` one. It does nothing while a main-loop turn runs or another prompt is on its way. It claims, submits with `$.prompt.submit({ text, asUser: true })`, and reports `started` from the main-loop `turn.start` whose text matches. A drop is reported as `dropped` with its reason. The loader requires every function that receives `$` to be declared at the top of the file, so the helpers take a small state object that `register()` creates.
- **Tests.** `tests/delivery.test.ts`, 7 tests; with the 13 in `cockpit.test.ts`, 20 pass. A hook in the test kit cannot raise `turn.start`, so the tests raise it, as the engine would, before letting the held submission enter. Each failure this task names was tried: submitting during a running turn (1 test fails), reporting before the turn starts (4 fail), submitting after a refused claim (1 fails), ignoring the kill switch (2 fail), and taking a subagent's turn for the main loop's (1 fails).
- **Live run.** An interactive Claude Code 2.1.299 in a private tmux session, with a scratch copy of the plugin carrying two probes, against a stand-in sidecar that logged every request. The plugin polled once a second with its real session ID.
  - Idle: a delivery added at :00.90 was claimed at :01.06, and its turn started at :01.16. Claude answered "pong". The terminal labels it "Prompt from the project-os-cockpit plugin".
  - Busy: a delivery added at :33.1 while a turn ran was claimed at :37.2, after that turn's Stop at :34.8. Its turn started 80 ms later.
- **The three facts.**
  - (a) **No.** The plugin's own `prompt.submit` hook never saw its own submission, though it saw a prompt typed by hand. So a prompt that is `sending` cannot be cancelled. TASK-0657 and the plan's Cancel section are updated.
  - (b) **Yes.** `classic.UserPromptSubmit` fired with the prompt's text, so the agent row shows it with no extra post.
  - (c) **Yes.** `turn.start`'s `text` was exactly the submitted text, with `asUser` set.
- **Validate.** `claude plugin validate`: passed with warnings, none new beyond the three new hooks' "gating hook without .catch".

