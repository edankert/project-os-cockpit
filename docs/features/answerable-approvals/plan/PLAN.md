---
type: "[[plan]]"
title: "Delivery plan: a permission prompt is answered from the cockpit"
status: active
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[FEAT-0159-A-Permission-Prompt-Is-Answered-From-The-Cockpit]]", "Edwin 2026-10-14: the three open questions answered (secret on two routes; agent:principal may answer; a 5 s wait, per workspace)"]
implements: ["[[FEAT-0159-A-Permission-Prompt-Is-Answered-From-The-Cockpit]]"]
related: ["[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]", "[[FEAT-0156-Claude-Sessions-Report-Through-The-Cockpit-Plugin]]", "[[FEAT-0158-A-Dispatched-Prompt-Is-Submitted-Not-Typed]]", "[[ISS-0301-A-Framed-Page-Can-Post-To-The-Loopback-Write-Endpoints]]", "[[RISK-0013-Approving-In-The-Cockpit-Runs-A-Command]]", "[[RISK-0012-A-Local-Request-Can-Put-A-Prompt-Into-A-Claude-Session]]", "[[RISK-0004-Hook-Injection-Surface]]", "[[RISK-0005-The-Write-Surface]]", "[[REQ-0026-Only-Human-Owned-Transitions]]", "[[REQ-0027-Every-Write-Guarded]]", "[[ADR-0009-The-Principal-Is-A-Role]]"]
---

<!-- Plans deliberately carry no `id:` / `aliases:`; see docs/__templates__/plan.md. -->
# Delivery plan: a permission prompt is answered from the cockpit

When a Claude session in a cockpit terminal asks permission to run a tool, the Needs you card will show the request with Approve and Deny buttons, and a click there is the session's answer. The session waits 5 seconds for that click. If none comes, the terminal shows its own permission prompt exactly as it does today. Nothing the cockpit sends can turn a refusal into a permission. Two sidecar routes, the one that answers and the one that puts a prompt into a Claude session, start requiring a secret that only the desktop shell holds. The work is four tasks.

## How permission prompts reach the cockpit today

- **The amber card is a session state, not a record.** The plugin forwards Claude Code's `PermissionRequest` hook to `/api/agent-hook`, and `agent_hooks.py` marks the session `needs-input`. The Needs you inbox in `renderer.ts` draws a card from that state. The card has no buttons; answering means finding the terminal.
- **The approvals store exists and nothing uses it.** `approvals.py` (`ApprovalStore`) can record a prompt and answer it, and the sidecar serves `GET /api/cockpit/approvals` and `POST /api/cockpit/approve` (`server.py`, `_serve_approve`). No client calls either route, and `record()` is called only from `tests/test_approvals.py`. So this feature builds the buttons and the recording; it does not wire up something that half-works.
- **`approvals.answer` checks a self-declared actor.** It refuses an actor starting `agent:` other than `agent:principal`, but the actor is whatever the request body says. The route's only other guards are loopback and the JSON `Content-Type` refusal ([[ISS-0301-A-Framed-Page-Can-Post-To-The-Loopback-Write-Endpoints]]).
- **`record()` cuts the prompt text at 1,000 characters.** That was harmless for a record. A person must never approve a command whose end they could not see, so this changes (step 2).

## What the mods interface gives, checked against the declarations

Checked against `desktop/plugin/claude-code/.claude-plugin/types/claude-code/index.d.ts`, the declarations Claude Code 2.1.299 writes. Claude Code 2.1.300 is installed.

- **`tool.check` fires after the `tool.call` and PreToolUse hooks, and before the mode settles an `ask`.** `next(e)` resolves to the engine's verdict (rules, mode, the tool's own check, PreToolUse's decision) and runs no tool. A hook may return any `{ decision }`.
- **So `classic.PermissionRequest` has not fired while the plugin waits.** The terminal shows nothing during the wait. If the plugin returns `allow` or `deny`, no terminal dialog appears at all; if it returns the original `ask`, the dialog appears as today.
- **A guard that fails is skipped and the verdict beneath stands.** A crash in the plugin therefore leaves the engine's own answer, which is what we want.
- **For a tool that requires the person, a hook's `allow` does not dismiss the dialog.** That covers a question put to the person (`AskUserQuestion`) and a plan to approve (`ExitPlanMode`). The plugin never offers those to the cockpit.
- **`e.tool_use_id` is present only on a real call.** A `$.tool.check` query has none, and the plugin never waits on a query.
- **`e.ceiling`** is the most permissive verdict the organization allows. When it is `ask`, a hook's `allow` cannot stand, so the plugin does not offer the call.
- **A hook has a 10 s limit, but time spent inside `$.http.fetch` or `$.clock.sleep` does not count toward it.** A 5 s wait fits either way.

## The flow, step by step

1. The model calls a tool. The plugin's `tool.check` hook calls `next(e)` first.
2. If the verdict is `allow` or `deny`, the hook returns it unchanged. **This is the rule that keeps a PreToolUse `deny` from being widened.**
3. If the verdict is `ask`, the hook offers the call to the cockpit only when all of these hold: the call is real (`tool_use_id` set), the tool is not `AskUserQuestion` or `ExitPlanMode`, `ceiling` is not `ask`, `decider` is not `host`, the kill switch is off, and the sidecar address is known. Otherwise it returns the `ask` unchanged.
4. It posts `POST /api/cockpit/approvals/ask` with the session ID, tool, full input, `tool_use_id` and `agentId`. The sidecar records an approval, publishes `cockpit:approval`, and answers `{approval_id, wait_ms}`. With `wait_ms` 0 (the workspace turned it off) or any error, the hook returns the `ask`.
5. The card appears on the Needs you list with the tool, the full command or file path, and Approve and Deny.
6. The hook reads `GET /api/cockpit/approvals?approval_id=<id>` every 250 ms until `wait_ms` has passed.
   - `granted`: it returns `{ decision: "allow", reason: "Approved in the cockpit by <actor>" }`.
   - `denied`: it returns `{ decision: "deny", reason: "Denied in the cockpit by <actor>" }`.
7. When the wait runs out, it posts `POST /api/cockpit/approvals/handed-back` with the approval ID. The sidecar moves an `open` approval to `handed-to-terminal` under its lock and returns the record. **If a click arrived first, the record is already `granted` or `denied`, and the hook uses that answer.** Only an approval that was still `open` is handed back, and then the hook returns the original `ask` and the terminal prompt appears.
8. On a `handed-to-terminal` card the buttons are gone and the card says "Answer in the terminal: the cockpit's 5 s wait ran out". A late click gets 409 and the same sentence.
9. The record closes (`closed`) when that session ends, or when a `PostToolUse` arrives with the same `tool_use_id`, and the card leaves the list. The existing one-hour `expired` status stays for a record nothing closed.

The same `tool_use_id` is never offered twice: `record()` becomes idempotent on `tool_use_id`, not on the prompt text.

## The secret

### What it guards

Edwin, 2026-10-14: the secret is required on the route that answers a permission prompt **and** the route that puts a prompt into a Claude session, and on no other route. The rest of the write routes stay under [[ISS-0301-A-Framed-Page-Can-Post-To-The-Loopback-Write-Endpoints]].

| Route | Caller | Secret required? | Why |
| --- | --- | --- | --- |
| `POST /api/cockpit/approve` | The shell's main process, from the card's buttons | **Yes** | An answer now runs a command. |
| `POST /api/cockpit/deliveries` | The shell's main process (`dispatch-queue.ts`, `handToSidecar`) | **Yes** | It takes prompt text and turns it into a Claude turn ([[RISK-0012-A-Local-Request-Can-Put-A-Prompt-Into-A-Claude-Session]]). |
| `POST /api/cockpit/deliveries/claim`, `/started`, `/dropped` | The plugin | No | They carry no prompt text, and the plugin must not hold the secret. |
| `POST /api/cockpit/deliveries/cancel` | The shell's main process | No | It can only withdraw a prompt, and Edwin scoped the secret to two routes. The main process could send it at no cost; that is a later choice, not this feature's. |
| `POST /api/cockpit/approvals/ask`, `/handed-back` | The plugin | No | They create a request or give one back to the terminal. Neither grants anything. |
| `POST /api/cockpit/dispatch` | The `cockpit dispatch` command, in any terminal | No | It carries a note ID and a verb, never prompt text. |

**The `cockpit dispatch` command keeps working, unchanged.** It posts to `/api/cockpit/dispatch`, which only records a request. The shell picks the request up, the renderer builds the prompt from the verb, and the main process posts the delivery with the secret. So the command never needs the secret, and agent terminals never get it. This is not an open question.

### How the secret reaches the sidecar

1. When the shell spawns a sidecar (`desktop/src/ipc/sidecar.ts`, `spawnSidecar`), it makes a new secret: 32 random bytes from `crypto.randomBytes`, as hex. It keeps it in that sidecar's record in memory only.
2. It spawns Python with `--secret-stdin` and `stdin: 'pipe'` (today `'ignore'`), writes one JSON line, `{"secret": "...", "approval_wait_ms": 5000}`, and closes standard input.
3. `__main__.py` reads that one line before the server starts, when and only when `--secret-stdin` is given, and passes both values to `make_server`. They live in the server's closure.
4. The secret is never in the sidecar's argv, its environment, a file under `.cockpit/`, the `hook-env` file, any terminal's environment, a log line, or any response.

**Why standard input.** On macOS a process can read the environment of another process run by the same user (`ps -E`), so an environment variable is readable by the agent. Standard input, closed after one line, is not.

**A sidecar started from a terminal** (`python -m project_os_cockpit docs`) has no secret. Both guarded routes then refuse every request with 403, "this server was started without the shell's secret". Nothing in that mode calls them today.

**Every spawn gets a new secret.** A sidecar the shell re-binds after a window reload keeps its record, and with it its secret. A sidecar that dies is respawned with a new one. Nothing persists it.

### How a request carries it

In a header, `X-Cockpit-Secret`, compared with `hmac.compare_digest`. A custom header also forces a browser to send a preflight, which the sidecar does not answer: one more reason a framed page cannot reach the route. Order of checks on both routes: loopback, JSON content type, secret, then the body. Missing or wrong secret: 403, with no hint about which.

### How the secret reaches the renderer: it does not

The card's buttons call a new IPC handler, `approval:answer(workspaceId, approvalId, decision)`, exposed in `preload.ts`. The main process posts to `/api/cockpit/approve` with the header and with `actor` set to `user:<the macOS account name>`. The renderer never holds the secret, so a script in a framed page or a note cannot read it from the window.

## Who may answer

Edwin, 2026-10-14: `agent:principal` may still answer a prompt that runs a command. `approvals.answer` keeps its current rule: it refuses any `agent:` actor other than `agent:principal`.

**What follows from combining that with the secret.** The route requires the shell's secret, and only the shell's main process holds it. The main process always answers as `user:<account>`. So a delegated principal ([[ADR-0009-The-Principal-Is-A-Role]]) can answer only through a path that holds the secret, and this feature builds no such path. The rule in `approvals.answer` is kept for the day one is built, for example by [[FEAT-0079-Supervision-From-A-Phone]] or a delegation runner, and that path will need its own decision about how it holds the secret.

This resolves the tension recorded in PHASE-046's impact analysis.

## The wait

Edwin, 2026-10-14: 5 seconds, configurable per workspace.

- The value is `approvalWaitMs` on the workspace's record in the shell's `workspaces.json` (in the app's user data folder). Absent means 5000. 0 turns cockpit answering off for that workspace: the plugin is told `wait_ms: 0` and returns the `ask` at once. Values are clamped to 0 to 30000.
- The shell passes it to the sidecar on the same standard-input line as the secret. The sidecar returns it on every `ask`. So a change takes effect when the sidecar is next spawned.
- **No settings screen in this feature.** The value is edited in `workspaces.json`. A screen can come later if Edwin wants one.

## Delivery sequence

1. **The secret** ([[TASK-0664-The-Sidecar-Requires-The-Shells-Secret-To-Answer-A-Prompt-Or-Deliver-One]]). `sidecar.ts` makes and sends it; `__main__.py` reads it; `server.py` requires it on the two routes; `dispatch-queue.ts` sends it on `handToSidecar`. Also the `approvalWaitMs` field and its passage to the sidecar, because it travels on the same line. After this task, dispatch to Claude works as before, and `POST /api/cockpit/approve` refuses any request without the secret.
2. **The plugin asks the cockpit before the terminal** ([[TASK-0665-The-Plugin-Asks-The-Cockpit-Before-The-Terminal-And-Never-Widens-A-Deny]]). The sidecar's `ask`, by-ID read and `handed-back` routes; the new statuses; closing on `PostToolUse` and `SessionEnd`; the full input kept (up to 16 KB; longer is not offered and the hook returns `ask`). The plugin's `tool.check` hook. `GET /api/cockpit/approvals` becomes loopback-only, because it now carries command text.
3. **The card answers** ([[TASK-0666-The-Needs-You-Card-Answers-A-Permission-Prompt]]). A Needs you card for each open or handed-back approval, drawn from `GET /api/cockpit/approvals` and the `cockpit:approval` event, with the full command, Approve and Deny, and the handed-back sentence. The `approval:answer` IPC handler in the main process.
4. **The guarantees, proved** ([[TASK-0667-Tests-Prove-A-Deny-Survives-And-An-Answer-Without-The-Secret-Is-Refused]]). The three tests Edwin's list names, each run with its guard removed to show it fails; the secret-leak sweep; capability register rows; the change note; [[TST-0096-A-Permission-Prompt-Is-Answered-From-The-Needs-You-Card]] made ready to run.

Each task carries its own unit tests. Task 4 holds the tests that prove the feature's promises end to end.

## Dependencies

- **Hard:** [[FEAT-0156-Claude-Sessions-Report-Through-The-Cockpit-Plugin]] (done): the plugin, its `hook-env` address and the kill switch.
- **Hard:** [[FEAT-0158-A-Dispatched-Prompt-Is-Submitted-Not-Typed]] (done): `handToSidecar` and the deliveries route that task 1 guards.
- **Hard:** Claude Code 2.1.299 or newer, as for FEAT-0158.
- **None on a later phase.** [[FEAT-0079-Supervision-From-A-Phone]] (a later answer path) is not needed and not built.

## Cost

While a prompt waits, the plugin makes one loopback GET every 250 ms, at most 20 for a 5 s wait. A person at the terminal waits up to 5 s longer before their own prompt appears; that is the trade Edwin chose, and 0 turns it off.

## Open question for Edwin

**Should the cards offer no buttons while the app runs with a Chrome debugging port?** A program connected to that port can press Approve as a person does, and the secret cannot tell the difference ([[RISK-0013-Approving-In-The-Cockpit-Runs-A-Command]]). The app has been started with `--remote-debugging-port=9222` for development. Recommendation: the main process checks `app.commandLine.hasSwitch('remote-debugging-port')`, and when it is set the card says "Answer in the terminal: the app was started with a debugging port". It is not in any task; it would be a small addition to TASK-0666. Nothing else in the plan depends on the answer.

## What the implementation must not do

- Change a `deny` or an `allow` that `next(e)` returned.
- Return `allow` for a call whose approval was not `granted` by a request carrying the secret.
- Put the secret anywhere the agent's terminal, the plugin or the renderer can read.
- Write a keystroke into a Claude terminal to answer a prompt.
- Require the secret on any route other than the two named.
- Write anything under `~/.claude` ([[RISK-0004-Hook-Injection-Surface]]).
