---
type: "[[plan]]"
title: "Delivery plan: a dispatched prompt is submitted, not typed"
status: active
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[FEAT-0158-A-Dispatched-Prompt-Is-Submitted-Not-Typed]]"]
implements: ["[[FEAT-0158-A-Dispatched-Prompt-Is-Submitted-Not-Typed]]"]
related: ["[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]", "[[FEAT-0025]]", "[[FEAT-0156-Claude-Sessions-Report-Through-The-Cockpit-Plugin]]", "[[RISK-0012-A-Local-Request-Can-Put-A-Prompt-Into-A-Claude-Session]]", "[[RISK-0004-Hook-Injection-Surface]]", "[[REQ-0027-Every-Write-Guarded]]", "[[REQ-0019-Agent-Fleet-Visibility]]"]
---

<!-- Plans deliberately carry no `id:` / `aliases:`; see docs/__templates__/plan.md. -->
# Delivery plan: a dispatched prompt is submitted, not typed

When a person dispatches a prompt to a Claude session from the cockpit, the cockpit will stop typing it into the terminal. The sidecar will hold it, the cockpit plugin inside the Claude session will submit it with `$.prompt.submit`, and the cockpit will mark it delivered only when the session's turn has started. Until that turn starts, the person can cancel it. Codex sessions, and dispatches that start a new `claude` or `codex` command in a plain shell, keep working as they do today. The work is four tasks.

## How dispatch works today

There are two ways in, and they meet in one function.

- **From the cockpit window.** A verb button, a selection, an inbox triage, a review answer or a request for changes builds a prompt in the renderer and calls `dispatch:execute` (`renderer.ts` `dispatchToAgent`, and four other callers that pass free text).
- **From the `cockpit dispatch` command.** It posts `{id, verb, agent, enqueue: true}` to `POST /api/cockpit/dispatch`. The sidecar keeps it in a take-once list. The renderer empties that list through `GET /api/cockpit/dispatch-requests`, builds the prompt from the verb, and calls `dispatch:execute` too (`renderer.ts` `drainDispatchRequests`). The request carries no prompt text, only a note ID and a verb.

So every dispatch reaches `executeDispatch` in the main process (`desktop/src/ipc/dispatch-queue.ts`). That function queues the item when the workspace is busy, and otherwise calls `deliver`, which writes into the terminal with `writeToPty`: `prompt + '\r'` for a waiting Claude session, a bracketed paste and a separate Return for Codex, or `<agent> '<prompt>'` for a plain shell. After writing, it posts the ledger entry (`recordLedger`, [[FEAT-0025]]), whose time is when the keystrokes were written.

**This changes the feature note's first candidate task.** The note worried that the plugin and the renderer would both empty the take-once list and steal each other's requests. They will not, because the plugin never reads that list. The plugin reads a new list of prompts already built and addressed to its session, which the main process fills. The `cockpit dispatch` command keeps its route through the renderer, because only the renderer can turn a verb into a prompt.

## What the mods interface gives, checked against the declarations

Checked against `desktop/plugin/claude-code/.claude-plugin/types/claude-code/index.d.ts`, the declarations Claude Code 2.1.299 writes, not against the web page.

- **`$.prompt.submit(args)`** takes `PromptSubmitArgs`: the prompt's `text`, and optionally `asUser: true`. It returns `Promise<PromptSubmitResult>`. The prompt "runs once the session is idle". The promise resolves "once the prompt entered the session and its turn started", with `{ text, ... }`, or with `{ drop: reason }` when a hook or the engine refused it.
- **It cannot be withdrawn.** It takes no `AbortSignal` and returns nothing else to hold on to. The `EventCalls` entry is `submit: (input: PromptSubmitArgs) => Promise<PromptSubmitResult>`, with no options argument. Once the plugin has called it, the plugin cannot take the prompt back through this call.
- **A `prompt.submit` hook can stop a prompt.** The hook fires "when a prompt is submitted, before the turn starts". It may return `{ drop: reason }` without calling `next`. A plugin's own submission "goes through every hook but the calling one (the plugin's others see it)", with `e.origin` set to `{ kind: 'plugin', name }`. This is the only point at which a submitted prompt can still be stopped. Whether a timer callback counts as "the calling one" is not stated, so task 2 tries it before task 4 relies on it.
- **`turn.start`** fires "when a model turn begins, main's or a subagent's (`e.agentId`), before its first model call". It carries `text` (the user's text) and `turnId`. A main-loop turn has no `agentId`.
- **`$.turn.abort({ turnId })`** cancels a running turn. That is stopping work already started, which this feature does not do (see Cancel, below).
- **`$.clock.every(ms, fn)`** runs `fn` every `ms` milliseconds until cancelled. The plugin starts it in its `session.start` hook, which fires once per process before the first prompt.

## A delivery, and its states

A **delivery** is one dispatched prompt on its way to one Claude session. The sidecar keeps the list, persisted with its sessions so a respawned sidecar still has it, capped at 30 per workspace. Each delivery has the dispatch item's fields (`id`, `rel`, `verb`, `agent`, `prompt`, `ts`), the session it is addressed to (`session_id`), a delivery ID of its own, and one of these states:

| State | What it means | What the person sees in the queue list |
| --- | --- | --- |
| `held` | No cockpit plugin has claimed the session, or the session ended before the prompt was submitted. Nothing will submit it. | "Not delivered: this Claude session has no cockpit plugin", or "Not delivered: the session ended" |
| `waiting` | The plugin will submit it once the session is idle. | "Waiting for Claude to finish its turn" |
| `sending` | The plugin has called `$.prompt.submit`; the turn has not started. | "Sending" |
| `cancelling` | The person cancelled while it was `sending`; the plugin's hook has not answered yet. | "Cancelling" |
| `started` | The session's turn started with this prompt. This is "delivered". | Leaves the list; the status line says "Delivered" |
| `cancelled` | The person cancelled it before its turn started. | Leaves the list; the status line says "Cancelled" |
| `dropped` | `$.prompt.submit` resolved with `{ drop }`, for example a UserPromptSubmit hook of the person's own blocked it. | "Not delivered: <the reason>" |

The sidecar makes every change of state under its lock, so two requests that race resolve one way only. A `held` delivery becomes `waiting` when the plugin claims its session; this covers a dispatch sent in the moment before the plugin's first post arrives. When the addressed session ends, `waiting` becomes `held` with the reason "the session ended". A held delivery is never sent to a different session; the person dispatches again.

## Delivery sequence

1. **The sidecar keeps deliveries** ([[TASK-0654-The-Sidecar-Keeps-A-List-Of-Prompts-Addressed-To-A-Claude-Session]]). The list and its states in `agent_hooks.py`, and these routes in `server.py`:
   - `POST /api/cockpit/deliveries`: the shell adds one. Body: the dispatch item and `session_id`. Starts `waiting` when the session is plugin-claimed, else `held`.
   - `GET /api/cockpit/deliveries`: every delivery not yet finished, for the shell; `?session=<id>` gives one session's, for the plugin. Reading does not remove anything.
   - `POST /api/cockpit/deliveries/<did>/claim`: the plugin, `waiting` to `sending`. Refused with 409 when the delivery is no longer `waiting`, which is how a cancel that arrived first wins.
   - `POST /api/cockpit/deliveries/<did>/started` with `{turn_id}`: the plugin, `sending` or `cancelling` to `started`. The ledger entry is written now, onto that exact session, with the turn's start time and `"delivered_by": "submit"`.
   - `POST /api/cockpit/deliveries/<did>/dropped` with `{reason}`.
   - Each change is published on the sidecar's event stream as `cockpit:delivery`, so the window updates without polling.
   - The session payload (`_slim`, `/api/cockpit/state`) gains `plugin_claimed`, so the shell can tell which sessions the plugin speaks for.
   - Every POST uses `_require_loopback` and the shared JSON reader, which refuses any other `Content-Type` ([[ISS-0301-A-Framed-Page-Can-Post-To-The-Loopback-Write-Endpoints]]). The routes change runtime state, not notes, so they join the named allow-list in `test_every_note_mutating_endpoint_requires_loopback` ([[RISK-0005-The-Write-Surface]]).
   - A capability register row for the routes.
2. **The plugin submits and confirms** ([[TASK-0655-The-Plugin-Submits-A-Waiting-Prompt-And-Confirms-When-Its-Turn-Starts]]). In `desktop/plugin/claude-code/hooks/register.ts`:
   - `session.start` starts a `$.clock.every(1000, ...)` poll of `GET /api/cockpit/deliveries?session=<own id>`. The address is read from `hook-env` each time, as every post already does. With `COCKPIT_NO_INSTRUMENT` set, or with no address, it polls nothing.
   - The plugin tracks whether a main-loop turn is running from `turn.start` and `turn.complete` (ignoring subagents). It handles one delivery at a time, oldest first, and only while no main-loop turn is running.
   - For that delivery it calls `claim`. On 409 it moves on. Otherwise it calls `$.prompt.submit({ text: prompt, asUser: true })`.
   - When a main-loop `turn.start` arrives whose `text` equals the submitted text, it posts `started` with that `turnId`. If the submit promise resolves with text and no matching `turn.start` was heard, it posts `started` with the next main-loop turn's ID. If it resolves with `{ drop }`, it posts `dropped` with the reason.
   - Three facts the declarations leave open, which this task checks in a real session before building on them: whether the plugin's own `prompt.submit` hook sees its own submission (task 4 needs this); whether `classic.UserPromptSubmit` fires for it, so the agent row shows the prompt (if not, the plugin posts that event itself on `started`); and whether `turn.start`'s `text` equals the submitted text when `asUser` is set.
   - `claude plugin test` cases that fail when a prompt is submitted during a running turn, when `started` is posted before the turn starts, or when a 409 claim is submitted anyway. A live run against a stand-in sidecar, recorded in the task note.
3. **The shell hands Claude dispatches to the sidecar** ([[TASK-0656-The-Shell-Sends-A-Claude-Dispatch-To-The-Sidecar-And-Types-Nothing]]). In `dispatch-queue.ts`:
   - `executeDispatch` asks the sidecar for the live session first. When it is a Claude session, the item is posted to `/api/cockpit/deliveries` with that `session_id`, whether the session is busy or waiting, because the plugin waits for idle itself. The `prompt + '\r'` write is removed.
   - Codex, and a workspace with no live session (the plain-shell branch that runs `claude '<prompt>'` or `codex '<prompt>'`), are unchanged, and so is their ledger entry. Their entries gain `"delivered_by": "typed"`, so the two meanings of the ledger's time can be told apart.
   - The queue chip and its list show deliveries beside the main-process queue, with the states in the table above. `queueDepthFor`, which the fleet view reads, counts unfinished deliveries too ([[REQ-0019-Agent-Fleet-Visibility]] asks for queue depth).
   - The "Delivered" status line comes from the `cockpit:delivery` event at `started`, not from the write.
   - Node tests for the routing decision: Claude goes to the sidecar, Codex is typed, no live session runs a command, and a Claude session the plugin does not claim is held and nothing is typed.
4. **Cancel** ([[TASK-0657-A-Dispatch-Can-Be-Cancelled-Until-Its-Turn-Starts]]). Below.

Cancel is after the submit-and-confirm task, as Edwin's change asked. It is last rather than third because the cancel button lives in the queue list that task 3 builds.

## Cancel

Edwin, 2026-10-14: "implement 2 please if we can ... would be good to know what this would look like". This section is what it looks like.

### What the person sees

- **Where the button is.** In the queue list that opens from the agent strip's `queued N` chip. Today that list has a `×` on each row of the main-process queue, labelled "Remove from queue". Each delivery that has not started gets the same `×`, labelled "Cancel". On a `held` or `dropped` row it reads "Remove", because nothing is on its way. "Clear all" cancels every row that has not started.
- **What each stage shows.** The row's text is the state's text from the table above. A dispatch held because no plugin claims the session also turns the chip amber and says `1 not delivered`, so it is not missed.
- **Cancelling a held, waiting or main-queue row.** The row disappears at once and the status line says "Cancelled <verb> <id>". Nothing reaches the session.
- **Cancelling a sending row.** The row says "Cancelling" for at most about a second. Then one of two things happens:
  - The plugin stopped it: the row disappears and the status line says "Cancelled <verb> <id>".
  - The turn started first: the row disappears and the status line says "Too late to cancel <verb> <id>: its turn started at 14:02. Press Esc in the terminal to stop it."
- **The note's dispatch history** shows a cancelled dispatch as cancelled, with the time, so a person reading the note later sees it was sent and withdrawn.

### How it works underneath, stage by stage

| Where the dispatch is | Can it be cancelled? | How |
| --- | --- | --- |
| In the main-process queue (Codex, or no terminal yet) | Yes | `dispatch:remove`, as today. |
| A delivery, `held` | Yes | `POST /api/cockpit/deliveries/<did>/cancel` sets `cancelled`. |
| A delivery, `waiting` | Yes | The same route sets `cancelled`. If the plugin's `claim` arrives afterwards it gets 409 and submits nothing. If the claim arrived first, the delivery is already `sending`; see the next row. |
| A delivery, `sending` | Only by the plugin's hook | The route sets `cancelling` and answers "pending". The plugin's own `prompt.submit` hook sees a submission with `origin.kind` `plugin`, this plugin's name and the text it is sending. It asks the sidecar for that delivery's state, within the hook's budget. When the state is `cancelling` it returns `{ drop: "Cancelled from the cockpit" }`, the submit promise resolves with that drop, and the plugin posts `dropped`, which the sidecar records as `cancelled`. If the hook cannot reach the sidecar in time, it lets the prompt through. |
| A delivery, `started` | No | The route answers 409 with the turn's start time. The turn is not aborted. |

**Why a started turn is not aborted.** `$.turn.abort` could stop it, but the turn may already have edited files, and an abort leaves the work half done without saying where. That is a different act from withdrawing a request, and Esc in the terminal already does it with the person watching. It can be added later if wanted.

**If the plugin's hook does not see its own submission.** Then the `sending` row cannot be cancelled, and the route answers "too late" for it. The window is short in practice: the plugin calls submit only when it has seen the session go idle, so `sending` lasts from that call to the turn's start. Task 2 finds out which case holds, and task 4 builds the one that does and records it in its note.

## The decisions the plan made

1. **The plugin reads a new list, not the take-once list.** Explained above. The `cockpit dispatch` command is unchanged.
2. **The prompt is submitted as the person's own words (`asUser: true`).** Today the typed prompt reads to the model as the person's, so the model sees no change. Hooks and the transcript still name the plugin as the origin. Without it the model would read "The project-os-cockpit plugin sent a message: …".
3. **The plugin submits only when it has seen the session idle,** even though `$.prompt.submit` would wait by itself. This keeps the stage that cannot be withdrawn as short as possible.
4. **A busy Claude session no longer waits in the main-process queue.** The delivery goes to the sidecar at once and the plugin waits for idle. The main-process queue keeps Codex and the no-terminal case.
5. **The ledger's delivered time is the turn's start for a submitted prompt,** and stays the write time for a typed one; `delivered_by` says which.
6. **No new secret on the new routes yet.** They are guarded like every other write: loopback only, and JSON only. [[RISK-0012-A-Local-Request-Can-Put-A-Prompt-Into-A-Claude-Session]] records what that leaves open. When [[FEAT-0159-A-Permission-Prompt-Is-Answered-From-The-Cockpit]] adds the shell's secret, `POST /api/cockpit/deliveries` should require it too.
7. **A delivery is never sent to another session.** If its session ends, it is held and the person dispatches again.
8. **No new requirement note.** The feature note's acceptance criteria and [[TST-0095-A-Prompt-Dispatched-To-Claude-Arrives-As-A-Submitted-Prompt-And-Can-Be-Cancelled]] carry the acceptance, as for FEAT-0156.

## Dependencies

- **Hard:** [[FEAT-0156-Claude-Sessions-Report-Through-The-Cockpit-Plugin]] (done): the plugin, its `hook-env` address, and the sidecar's `plugin_claimed` mark.
- **Hard:** Claude Code 2.1.299 or newer. Edwin, 2026-10-14: everyone will be on that version, so nothing handles an older one.
- **Soft:** [[ISS-0301-A-Framed-Page-Can-Post-To-The-Loopback-Write-Endpoints]]'s Content-Type refusal, already committed, is what keeps a web page from posting a delivery.

## Cost

The plugin polls the sidecar once a second in every cockpit Claude session. That is one small loopback GET per second per session, and nothing when the kill switch is set. No new long-running step.

## What the implementation must not do

- Write a prompt into a Claude session's terminal by any path.
- Change what Codex receives, or the plain-shell branch.
- Change the `cockpit dispatch` command's route or the take-once list.
- Abort a running turn.
- Write anything under `~/.claude` ([[RISK-0004-Hook-Injection-Surface]]).
