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
  - "[[TASK-0658-A-Waiting-Prompt-Survives-The-Person-Pressing-Esc]]"
  - "[[TASK-0659-A-Prompt-Held-After-Esc-Says-Claude-Is-Waiting-For-You]]"
  - "[[TASK-0660-A-Dispatch-Checks-What-Runs-In-The-Terminal-Before-Typing]]"
  - "[[TASK-0661-Every-Project-Uses-One-Codex-Hook-Command]]"
  - "[[TASK-0662-Review-Round-One-A-Prompt-Unconfirmed-At-Session-End-Is-Not-Called-Cancelled]]"
release: ""
acceptance_exception: ""
acceptance: "[[TST-0095-A-Prompt-Dispatched-To-Claude-Arrives-As-A-Submitted-Prompt-And-Can-Be-Cancelled]]"
design: ""
reviewed_by: ["model:claude-opus-5-5 (independent-reviewer, round 1, A)", "model:claude-opus-5-5 (independent-reviewer, round 1, B)"]
review_date: 2026-10-14
review_verdict: changes-requested
review_round: 1
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

**Built and accepted; waiting for the independent review.** All eight tasks are done. TST-0095 passed all ten steps on 2026-10-14 (ledger: pass on macOS, Edwin). Running it produced four of the tasks: TASK-0658 and TASK-0659 (a prompt waiting when the person presses Esc is held until their next message, and the cockpit says so), TASK-0660 (a dispatch reads the terminal's foreground program before typing, so it never types a shell command into a running agent; fixes ISS-0322 and ISS-0321) and TASK-0661 (every project's Codex hooks run one command, so one trust in Codex covers them all). What changed is in [[CHG-20261014-A-Prompt-Dispatched-To-Claude-Is-Submitted-Not-Typed]].

One finding changed the cancel design. A plugin's own `prompt.submit` hook never sees its own submission, so a prompt the plugin has handed to Claude cannot be withdrawn. Cancel works until the plugin claims the prompt; after that, the cockpit says it is too late. In the live run, that window was about 100 ms.

## Verification

Full runs on 2026-10-14 at 3e8eab5, after all eight tasks:

- `.venv/bin/python -m pytest -q -p no:randomly`: 2168 passed, 10 skipped.
- `node --test desktop/tests/*.test.mjs`, after `npm run build`: 211 passed.
- `npx tsc --noEmit` in `desktop/`: clean.
- `command claude plugin test desktop/plugin/claude-code` with Claude Code 2.1.299: 22 passed.
- `command claude plugin validate desktop/plugin/claude-code`: passed with warnings.
- `bash tools/scripts/validate-docs.sh`: OK.
- [[TST-0095-A-Prompt-Dispatched-To-Claude-Arrives-As-A-Submitted-Prompt-And-Can-Be-Cancelled]]: pass, all ten steps, Edwin, macOS.

After the round 1 fixes (TASK-0662): pytest 2171 passed, 11 skipped; desktop 214 passed; plugin 23 passed; `tsc` clean; `claude plugin validate` passed with warnings.

## Review

**Round 1, 2026-10-14: `changes-requested`.** Two `independent-reviewer` subagents ran on the same packet (`review-packet.py FEAT-0158`, two author claims), each in a fresh context, with 30 and 32 tool calls. Both ran on the same model as the author. The packet's diff was 1,987 lines, over the 1,500-line warning, accepted knowingly. A refutation with evidence decides a claim.

| # | Criterion | Combined verdict | Evidence |
|---|---|---|---|
| 1 | Submitted through `$.prompt.submit`; nothing typed | holds | Both: `routeFor` returns `submit` first; B changed `routeFor`'s last `hold` to `shell` and 3 desktop tests failed. |
| 2 | Read as the person's own words | holds in code; **no automated guard** | `asUser: true` at `register.ts:210`. B set it to `false` and all 22 plugin tests passed. Fixed: TASK-0662 adds a test. |
| 3 | Ledger records it only when its turn starts, on that session, at the turn's start | **refuted** (edge case) | A: claim, then `SessionEnd`, moved the `sending` prompt to `held`; the plugin's started report was then refused, so a turn that may have run was never recorded. Reproduced by the author. Normal path holds (B's mutation failed the ledger test). Fixed: TASK-0662. |
| 4 | Submitted after the running turn, never during it | holds | Both removed the `mainTurnRunning` checks; 2 plugin tests failed. |
| 5 | Unclaimed session: held, shown, never typed | holds | Both; B's claim-from-held mutation failed a test. |
| 6 | (amended) shell / Codex / anything else | holds, each part | Both; A's and B's `hold`→`shell` mutation failed 3 tests. |
| 7 | Cancel before the turn starts; a cancelled prompt never starts a turn; a late cancel says so | **refuted** (edge case) | A: in the case under 3, a cancel was then accepted and the history said "cancelled, before it reached the session" for a prompt that may have run. B's mutation of the `sending` refusal failed 3 tests. Fixed: TASK-0662. |
| 8 | Loopback-only and JSON-only routes | holds | Both; B removed the claim route's loopback guard and 3 tests failed. |
| 9 | Fleet queue depth counts the sidecar's prompts | holds in code; **shell half untested** | Sidecar half tested; `agents-fleet.ts` line had no test. Fixed: TASK-0662 adds one. |
| T | TST-0095 guards the behaviour | holds as a manual check | Both said its record was stale. The status stays `active`: an acceptance check's verdict is in the release ledger, not on the note (STATUSES.md, "`level: acceptance`"), and the ledger has it. The "(in progress)" heading and the missing tasks were fixed. |
| A1 | Never a shell command into a non-shell foreground | holds | Both, same mutation as 6. A noted the terminal is read once, up to 3 s before typing. |
| A2 | Identical Codex hook commands, stale launchers included | holds | Both; tests for both halves pass. |

**The packet left out two central commits**, `ac251c2` (TASK-0655) and `3d02c05` (TASK-0656), because their subjects name no ID the packet searched for. Both reviewers read them from git. Round 2's packet uses `--since`.

**Other observations, and what became of them.** Fixed in TASK-0662: the plugin never retried its started report (A); held and dropped prompts filled the 30-prompt cap (A and B); "Clear all" on a dropped prompt wrote "cancelled, before it reached the session" (A). Kept, with the reason in TASK-0662: no re-check of a running turn after the claim (`$.prompt.submit` waits for idle itself); a submit with no `turn.start` reports the next turn (A and B; the TASK-0655 design); a launcher that does not `exec` would look like a shell (B); with two live Claude sessions the state's session is chosen (B; predates this feature); an interruption sticks for Claude until the next prompt (A; that is TASK-0659's rule). Not acted on: `cancelling` is still handled in `deliveryRowText` though unused (B).

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
6. Codex sessions and the plain-shell branch receive exactly what they do today. *Amended 2026-10-14 by TASK-0660 (Edwin: "yes, implement both parts"):* the cockpit reads the terminal's foreground program before typing. A shell receives `<agent> '<prompt>'` exactly as before; a running Codex receives the prompt pasted with a separate Return, as before, now also when it has not yet reported to the cockpit; anything else, including a Claude the cockpit cannot reach, is held and never typed into.
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
