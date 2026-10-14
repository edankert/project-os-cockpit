---
type: "[[task]]"
id: TASK-0665
aliases: ["TASK-0665"]
title: "The plugin offers a Claude permission ask to the cockpit, waits 5 s for an answer, hands it to the terminal if none comes, and never changes an allow or a deny"
status: done
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

- [x] **The sidecar.** `POST /api/cockpit/approvals/ask` (loopback, JSON, no secret): body `{session_id, tool, input, tool_use_id, agent_id?}`. It records an approval and answers `{approval_id, wait_ms}`, and publishes `cockpit:approval`. `record()` is idempotent on `tool_use_id`. It keeps the input in full up to 16 KB; above that it records nothing and answers `wait_ms: 0`, so a person never approves a command they could not read in full.
- [x] `GET /api/cockpit/approvals?approval_id=<id>` returns that one record. `GET /api/cockpit/approvals` with or without the parameter is loopback-only, because it carries command text.
- [x] `POST /api/cockpit/approvals/handed-back` with `{approval_id}` moves an `open` approval to `handed-to-terminal` under the store's lock, and returns the record whatever its status, so a click that arrived first wins.
- [x] `approvals.answer` answers only an `open` approval. For `handed-to-terminal` the route answers 409 with "Answer in the terminal: the cockpit's wait ran out".
- [x] The statuses gain `handed-to-terminal` and `closed`. An `open` or `handed-to-terminal` approval becomes `closed` when its session ends or a `PostToolUse` with its `tool_use_id` arrives at `/api/agent-hook`. `escalation.sweep` still counts `open` ones.
- [x] **The plugin.** In `desktop/plugin/claude-code/hooks/register.ts`, `on('tool.check', ...)` calls `next(e)` first and returns its result unchanged unless it is `ask`.
- [x] It offers an `ask` only for a real call (`e.tool_use_id` set), not for `AskUserQuestion` or `ExitPlanMode`, not when `e.ceiling` is `ask`, not when the verdict's `decider` is `host`, not under `COCKPIT_NO_INSTRUMENT`, and not when `hook-env` gives no address. Otherwise it returns the `ask`.
- [x] It polls the approval every 250 ms with `$.clock.sleep` and `$.http.fetch` until `wait_ms` passes. `granted` returns `{decision: 'allow', reason}`; `denied` returns `{decision: 'deny', reason}`; otherwise it posts `handed-back` and uses the record that returns: `granted` or `denied` as above, anything else the original `ask`. Any error at any point returns the original `ask`.
- [x] The hook has a `.catch` that returns the verdict beneath, so a fault never widens anything.
- [x] The plugin does not hold, read or send the secret.
- [x] pytest cases for the routes: an approval recorded twice for one `tool_use_id` is one record; `handed-back` after a grant returns the grant; an answer after `handed-back` is refused; an input over 16 KB is not offered; `PostToolUse` closes the record; the list is refused to a remote peer.
- [x] `claude plugin test` cases that fail when: the hook changes an `allow` or a `deny` from `next(e)`; it waits on a query (no `tool_use_id`); it offers `AskUserQuestion`; it returns `allow` after the wait ran out with the record still `open`; it returns anything but the original `ask` when the sidecar cannot be reached.
- [x] A live run in a real Claude session against a stand-in sidecar, recorded in this note: a Bash call that asks, granted within the wait (no terminal dialog appears), denied within the wait, and left to run out (the terminal dialog appears after about 5 s).

## Steps

- [x] The store's states, full input and closing.
- [x] The three routes.
- [x] The hook.
- [x] Tests and the live run.

## Notes

- Three facts the declarations leave open, which the live run checks before the card is built: whether `PostToolUse` carries `tool_use_id` in the plugin's forwarded payload; whether `classic.PermissionRequest` still fires for a call the hook answered (the declarations say the mode never settles the ask, so it should not); and whether the `reason` on an `allow` is shown anywhere.
- The `deny` reason is what the model reads. Keep it plain: "Denied in the cockpit by user:edwin."

## Built, 2026-10-14

**What a person notices:** nothing yet, because no card draws these approvals until TASK-0666. A Claude session in a cockpit terminal now waits up to 5 s before showing a permission dialog, but only in manual (`default`) or `acceptEdits` mode, and only when the sidecar is reachable.

- **The sidecar.** `approvals.py` gains `ask` (idempotent on `tool_use_id`, the input kept whole up to `MAX_INPUT_BYTES`, the card's text from `summary`), `get`, `hand_back`, `close` and `answer_open`, and the statuses `handed-to-terminal` and `closed`. `server.py` gains `POST /api/cockpit/approvals/ask` and `/handed-back`, `GET /api/cockpit/approvals?approval_id=`, and makes the list loopback-only. A late or second answer gets 409. Tests: `tests/test_approval_ask.py` (12) and the remote-peer sweep (38 guard sites, 34 guarded POST routes, each change dated there).
- **The plugin.** `on('tool.check', ...)` in `register.ts`, with `.catch(($, e, next) => next(e))`. `offerable` and `cockpitVerdict` are exported for the tests. `tests/approval.test.ts` has 16 cases. Removing any one of the eight guards (the decision, the tool call, person-only tools, the ceiling, a host decider, the mode, the hand-back fallback, the denial) fails at least one of them.
- **Changed by the live run: the permission mode.** The first live run was in auto mode. The plugin offered a Bash call, waited the full 5 s, handed it back, and then the classifier allowed it. Every classified call would have been 5 s slower for nothing. The plugin now remembers `permission_mode` from each classic event it forwards and offers an ask only in `default` or `acceptEdits`, where a person is asked. In `auto`, `dontAsk`, `plan`, `bypassPermissions`, or before any event has said the mode, it returns the ask unchanged.
- **Changed by the live run: closing a prompt refused in the terminal.** Esc on the terminal's dialog sent no hook event at all: no `Stop`, no `Interrupt`. The record stayed `handed-to-terminal` until the session ended. The sidecar now also closes a session's main-loop records on `Stop`, `Interrupt` and `UserPromptSubmit`; a subagent's (`agent_id` set) are left open, because a background subagent can outlive the turn.

### The live run, 2026-10-14, Claude Code 2.1.300

A real interactive session in a tmux pane, with `CLAUDE_CODE_PLUGIN_DIRS` on this plugin and `COCKPIT_INSTRUMENT_DIR` on a scratch folder whose `hook-env` named a stand-in sidecar started with `--secret-stdin`. Answers were sent with `curl` carrying the secret, standing in for the card.

| Case | Result |
| --- | --- |
| Auto mode, before the mode check | Offered, 5 s wait, handed back, then allowed by the classifier. Led to the mode check above. |
| Manual mode, granted within the wait | `touch probe-granted.txt` ran. No terminal dialog appeared. |
| Manual mode, denied within the wait | The file was not created. The model reported "Denied in the cockpit by user:edwin." The session never showed `needs-input`. |
| Manual mode, no answer | The terminal dialog appeared 5.0 s after the offer. A click after that got 409, "Answer in the terminal: the cockpit's wait ran out". |
| Refused with Esc in the terminal | No event was sent; the record closed on the next prompt (after the change above). |

The three facts the plan left open:

1. **`PostToolUse` carries `tool_use_id`** in the payload the plugin forwards: the auto-mode record closed when its call ran.
2. **`classic.PermissionRequest` does not fire for a call the hook answered.** The session's state stream showed only `busy` and `waiting` during the denied case, and `needs-input` only when the dialog appeared.
3. **The reason on an `allow` is not shown** in the terminal; the transcript shows "Ran 1 shell command". The reason on a `deny` is what the model reads.
