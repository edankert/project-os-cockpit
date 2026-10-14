---
type: "[[feature]]"
id: FEAT-0158
aliases: ["FEAT-0158"]
title: "A prompt dispatched from the cockpit reaches a Claude session as a submitted prompt, confirmed when its turn starts, instead of as typed keystrokes"
status: doing
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-08
updated: 2026-10-14
source:
  - "Edwin 2026-10-08: 'Plan the implementation in a new phase.'"
  - "[[REFERENCE-FUNCTION-HOOKS-REVIEW]], 'Dispatch is a robot typing into a terminal'"
  - "Edwin 2026-10-14: 'start FEAT-0158'"
  - "Edwin 2026-10-14: 'implement 2 please if we can ... would be good to know what this would look like'"
goal: "When a person dispatches a prompt to a Claude session from the cockpit, the session receives it as a submitted prompt, and the cockpit records it as delivered only once the session's turn has started."
requirements: []
tasks:
  - "[[TASK-0654-The-Sidecar-Keeps-A-List-Of-Prompts-Addressed-To-A-Claude-Session]]"
  - "[[TASK-0655-The-Plugin-Submits-A-Waiting-Prompt-And-Confirms-When-Its-Turn-Starts]]"
  - "[[TASK-0656-The-Shell-Sends-A-Claude-Dispatch-To-The-Sidecar-And-Types-Nothing]]"
  - "[[TASK-0657-A-Dispatch-Can-Be-Cancelled-Until-Its-Turn-Starts]]"
release: ""
acceptance_exception: ""
acceptance: "[[TST-0095-A-Prompt-Dispatched-To-Claude-Arrives-As-A-Submitted-Prompt-And-Can-Be-Cancelled]]"
design: ""
related:
  - "[[FEAT-0025]]"
  - "[[FEAT-0156-Claude-Sessions-Report-Through-The-Cockpit-Plugin]]"
  - "[[PHASE-040-The-Agent-Session-Is-Not-A-Terminal]]"
  - "[[RISK-0012-A-Local-Request-Can-Put-A-Prompt-Into-A-Claude-Session]]"
  - "[[RISK-0004-Hook-Injection-Surface]]"
  - "[[REQ-0019-Agent-Fleet-Visibility]]"
  - "[[REQ-0027-Every-Write-Guarded]]"
---

# A dispatched prompt is submitted, not typed

**Started 2026-10-14.** FEAT-0156's plugin is done, so this feature can use it. The plan, checked against the declarations Claude Code 2.1.299 writes, is `plan/PLAN.md` beside this note. The work is four tasks:

1. [[TASK-0654-The-Sidecar-Keeps-A-List-Of-Prompts-Addressed-To-A-Claude-Session]]: the sidecar keeps each dispatched prompt for its session, with its state.
2. [[TASK-0655-The-Plugin-Submits-A-Waiting-Prompt-And-Confirms-When-Its-Turn-Starts]]: the plugin submits it when the session is idle, and confirms when the turn starts.
3. [[TASK-0656-The-Shell-Sends-A-Claude-Dispatch-To-The-Sidecar-And-Types-Nothing]]: the shell stops typing into Claude sessions and shows each dispatch's state.
4. [[TASK-0657-A-Dispatch-Can-Be-Cancelled-Until-Its-Turn-Starts]]: the person can cancel a dispatch until its turn starts.

The acceptance check is [[TST-0095-A-Prompt-Dispatched-To-Claude-Arrives-As-A-Submitted-Prompt-And-Can-Be-Cancelled]].

## State on 2026-10-14

**Built; waiting for Edwin's acceptance run.** All four tasks are done, and what changed is in [[CHG-20261014-A-Prompt-Dispatched-To-Claude-Is-Submitted-Not-Typed]]. The plugin's part was tried in a real interactive Claude session against a stand-in sidecar. The queue list and its buttons have not been seen in the running application. [[TST-0095-A-Prompt-Dispatched-To-Claude-Arrives-As-A-Submitted-Prompt-And-Can-Be-Cancelled]] is Edwin's to run after `npm run build` in `desktop/` and a restart; the independent review comes after it.

One finding changed the cancel design. A plugin's own `prompt.submit` hook never sees its own submission, so a prompt the plugin has handed to Claude cannot be withdrawn. Cancel works until the plugin claims the prompt; after that, the cockpit says it is too late. In the live run, that window was about 100 ms.

## Verification

Full runs on 2026-10-14, after all four tasks:

- `python3 -m pytest -q -p no:randomly`: 2166 passed, 11 skipped.
- `node --test desktop/tests/*.test.mjs`, after `npm run build`: 202 passed.
- `npx tsc --noEmit` in `desktop/`: clean.
- `command claude plugin test desktop/plugin/claude-code` with Claude Code 2.1.299 and an empty HOME: 20 passed.
- `command claude plugin validate desktop/plugin/claude-code`: passed with warnings.
- `bash tools/scripts/validate-docs.sh`: OK.

## Decisions, 2026-10-14

1. **A dispatch to a Claude session that no plugin claims is held and shown as undelivered.** It is never typed instead. Edwin settled this on 2026-10-14 by taking the note's recommendation (open question 1 below). Asked "Shall I start FEAT-0158 with those two defaults?", where the first default was to hold and show an unclaimed dispatch, he answered "start FEAT-0158".
2. **Cancelling a dispatch before its turn starts is in scope.** Edwin first took the recommendation to leave it out, then changed it the same day: "implement 2 please if we can ... would be good to know what this would look like". What it looks like, and the one stage where a submitted prompt cannot be taken back, is the plan's "Cancel" section.
3. **No handling for Claude Code older than 2.1.299.** Edwin, 2026-10-14: everyone will be on Claude Code 2.1.299 or newer (the same decision closed [[ISS-0318]]).

## Acceptance Criteria

1. A prompt dispatched to a Claude session the plugin claims reaches the session through `$.prompt.submit`. No code path writes it into the terminal.
2. The model reads it as the person's own words, as it did when it was typed.
3. The dispatch ledger records it as delivered only when the session's turn has started, on that session, with the turn's start time.
4. A prompt dispatched while the session is busy is submitted after the running turn ends, and never during it.
5. A prompt dispatched to a Claude session no plugin claims is held, shown as not delivered, and never typed.
6. Codex sessions and the plain-shell branch receive exactly what they do today.
7. The person can cancel a dispatch at any stage before its turn starts at which the plan says it can be withdrawn, and a cancelled prompt never starts a turn. A cancel that arrives after the turn started says so, with the time, and does not stop the turn.
8. The new sidecar routes refuse a request that does not come from this machine or is not JSON.
9. The fleet view's queue depth counts dispatches waiting in the sidecar as well as those in the shell's queue.

## Goal

Today a dispatched prompt is typed into the terminal: `desktop/src/ipc/dispatch-queue.ts:189` writes `item.prompt + '\r'` into the pseudo-terminal. So a dispatch cannot be confirmed, and the session cannot tell it from a person typing. After this feature, the cockpit's plugin inside the Claude session takes the prompt and calls `$.prompt.submit`, which waits until the session is idle and then starts a turn. The plugin tells the sidecar when that turn starts, and only then is the dispatch recorded as delivered. Codex sessions keep the typed path.

## Findings

- **Two routes reach the terminal today.** Dispatches started in the shell go through `dispatch-queue.ts` over IPC straight to the PTY. Dispatches started from the `cockpit dispatch` command are queued in the sidecar, and the renderer drains them from `GET /api/cockpit/dispatch-requests` (`renderer.ts:17598`). Both have to reach the plugin for a Claude session.
- **The sidecar queue is take-once.** `take_dispatch_requests()` (`agent_hooks.py:587`) empties the list for whoever asks first. If the plugin and the renderer both poll it, each will steal the other's requests. So requests need a session address, and each consumer takes only its own. That is a change to the sidecar contract, and the capability register needs a row for it.
- **What the plugin does.** A `$.clock.every` timer fetches requests for its session, calls `$.prompt.submit({text})`, and posts a confirmation when `turn.start` fires for that prompt. The dispatch ledger ([[FEAT-0025]]) then gets a real delivered time instead of the time keystrokes were written.
- **Codex.** `dispatch-queue.ts` keeps its Codex branch (the bracketed-paste write) and its shell-mode branch, which starts a new `claude` or `codex` command. Only the Claude REPL branch moves.
- **[[PHASE-040-The-Agent-Session-Is-Not-A-Terminal]]** (deferred) would hand session ownership to T3 Code and dispatch through it. This feature does not block that: if PHASE-040 is reopened, it replaces this route the same way it replaces the PTY one.

### Candidate tasks, as filed on 2026-10-08

Minted on 2026-10-14 as the four tasks above. The first changed: the plugin reads a new list of prompts the shell has already built, not the take-once request list, so the two never compete (plan, "How dispatch works today").

1. Address dispatch requests to a session in the sidecar, so each consumer takes only its own.
2. The plugin's poll, submit and confirm, with the ledger stamped on `turn.start`.
3. Route the shell's own Claude REPL dispatches through the sidecar to the plugin, and remove the Claude `prompt + '\r'` write.

## Open questions

Both answered on 2026-10-14; see Decisions above.

1. **What happens to a request no plugin claims?** For example, a Claude session started with the kill switch on, or with an older Claude Code. Options: fall back to typing it, or hold it and show it as undelivered. Recommendation: hold and show it, because a silent fallback brings back the unconfirmable path.
2. **Can a dispatch be cancelled before its turn starts?** `$.prompt.submit` waits for the session to be idle, so there is a window. Cancelling it is new capability; it is out of scope unless Edwin wants it now.

## Links

- Phase: [[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]
- Code: `desktop/src/ipc/dispatch-queue.ts`, `src/project_os_cockpit/agent_hooks.py` (`take_dispatch_requests`), `src/project_os_cockpit/server.py` (`_serve_dispatch_requests`)
