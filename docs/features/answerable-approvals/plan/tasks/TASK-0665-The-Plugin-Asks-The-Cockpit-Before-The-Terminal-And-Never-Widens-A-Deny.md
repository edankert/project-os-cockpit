---
type: "[[task]]"
id: TASK-0665
aliases: ["TASK-0665"]
title: "The plugin offers a Claude permission ask to the cockpit, waits 5 s for an answer, hands it to the terminal if none comes, and never changes an allow or a deny"
status: backlog
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[FEAT-0159-A-Permission-Prompt-Is-Answered-From-The-Cockpit]], candidate task 2", "plan/PLAN.md, 'The flow, step by step' and 'The wait'"]
parent: "[[FEAT-0159-A-Permission-Prompt-Is-Answered-From-The-Cockpit]]"
effort: "L"
due: ""
depends: ["[[TASK-0664-The-Sidecar-Requires-The-Shells-Secret-To-Answer-A-Prompt-Or-Deliver-One]]"]
blocks: ["[[TASK-0666-The-Needs-You-Card-Answers-A-Permission-Prompt]]"]
related: ["[[RISK-0013-Approving-In-The-Cockpit-Runs-A-Command]]", "[[RISK-0004-Hook-Injection-Surface]]", "[[RISK-0006-The-Unattended-Worker]]", "[[FEAT-0076]]"]
tests: []
---

# The plugin asks the cockpit before the terminal

The cockpit plugin gains a `tool.check` hook. It asks Claude Code's own rules first. Only when they answer `ask` does it record an approval in the sidecar and wait for the person's click, for the workspace's wait (5 s by default). It returns the click's answer, or the original `ask` when the wait runs out. The sidecar gains the routes the plugin needs, and its approvals store gains the states and the full command text.

## Definition of Done

- [ ] **The sidecar.** `POST /api/cockpit/approvals/ask` (loopback, JSON, no secret): body `{session_id, tool, input, tool_use_id, agent_id?}`. It records an approval and answers `{approval_id, wait_ms}`, and publishes `cockpit:approval`. `record()` is idempotent on `tool_use_id`. It keeps the input in full up to 16 KB; above that it records nothing and answers `wait_ms: 0`, so a person never approves a command they could not read in full.
- [ ] `GET /api/cockpit/approvals?approval_id=<id>` returns that one record. `GET /api/cockpit/approvals` with or without the parameter is loopback-only, because it carries command text.
- [ ] `POST /api/cockpit/approvals/handed-back` with `{approval_id}` moves an `open` approval to `handed-to-terminal` under the store's lock, and returns the record whatever its status, so a click that arrived first wins.
- [ ] `approvals.answer` answers only an `open` approval. For `handed-to-terminal` the route answers 409 with "Answer in the terminal: the cockpit's wait ran out".
- [ ] The statuses gain `handed-to-terminal` and `closed`. An `open` or `handed-to-terminal` approval becomes `closed` when its session ends or a `PostToolUse` with its `tool_use_id` arrives at `/api/agent-hook`. `escalation.sweep` still counts `open` ones.
- [ ] **The plugin.** In `desktop/plugin/claude-code/hooks/register.ts`, `on('tool.check', ...)` calls `next(e)` first and returns its result unchanged unless it is `ask`.
- [ ] It offers an `ask` only for a real call (`e.tool_use_id` set), not for `AskUserQuestion` or `ExitPlanMode`, not when `e.ceiling` is `ask`, not when the verdict's `decider` is `host`, not under `COCKPIT_NO_INSTRUMENT`, and not when `hook-env` gives no address. Otherwise it returns the `ask`.
- [ ] It polls the approval every 250 ms with `$.clock.sleep` and `$.http.fetch` until `wait_ms` passes. `granted` returns `{decision: 'allow', reason}`; `denied` returns `{decision: 'deny', reason}`; otherwise it posts `handed-back` and uses the record that returns: `granted` or `denied` as above, anything else the original `ask`. Any error at any point returns the original `ask`.
- [ ] The hook has a `.catch` that returns the verdict beneath, so a fault never widens anything.
- [ ] The plugin does not hold, read or send the secret.
- [ ] pytest cases for the routes: an approval recorded twice for one `tool_use_id` is one record; `handed-back` after a grant returns the grant; an answer after `handed-back` is refused; an input over 16 KB is not offered; `PostToolUse` closes the record; the list is refused to a remote peer.
- [ ] `claude plugin test` cases that fail when: the hook changes an `allow` or a `deny` from `next(e)`; it waits on a query (no `tool_use_id`); it offers `AskUserQuestion`; it returns `allow` after the wait ran out with the record still `open`; it returns anything but the original `ask` when the sidecar cannot be reached.
- [ ] A live run in a real Claude session against a stand-in sidecar, recorded in this note: a Bash call that asks, granted within the wait (no terminal dialog appears), denied within the wait, and left to run out (the terminal dialog appears after about 5 s).

## Steps

- [ ] The store's states, full input and closing.
- [ ] The three routes.
- [ ] The hook.
- [ ] Tests and the live run.

## Notes

- Three facts the declarations leave open, which the live run checks before the card is built: whether `PostToolUse` carries `tool_use_id` in the plugin's forwarded payload; whether `classic.PermissionRequest` still fires for a call the hook answered (the declarations say the mode never settles the ask, so it should not); and whether the `reason` on an `allow` is shown anywhere.
- The `deny` reason is what the model reads. Keep it plain: "Denied in the cockpit by user:edwin."
