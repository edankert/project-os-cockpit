---
type: "[[feature]]"
id: FEAT-0159
aliases: ["FEAT-0159"]
title: "A Claude Code permission prompt can be answered from the cockpit, by a person, and the answer never overrides a deny"
status: doing
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-08
updated: 2026-10-21
source:
  - "Edwin 2026-10-08: 'Plan the implementation in a new phase.'"
  - "[[REFERENCE-FUNCTION-HOOKS-REVIEW]], the paragraph on permission prompts"
  - "Edwin 2026-10-14: 'Continue PHASE-046', and his answers to the three open questions"
goal: "When a Claude session asks permission to use a tool, the person can approve or deny it with the cockpit's buttons, and that click is the session's answer; nobody else can answer it, and nothing the cockpit sends can turn a deny into an allow."
requirements: []
tasks:
  - "[[TASK-0664-The-Sidecar-Requires-The-Shells-Secret-To-Answer-A-Prompt-Or-Deliver-One]]"
  - "[[TASK-0665-The-Plugin-Asks-The-Cockpit-Before-The-Terminal-And-Never-Widens-A-Deny]]"
  - "[[TASK-0666-The-Needs-You-Card-Answers-A-Permission-Prompt]]"
  - "[[TASK-0667-Tests-Prove-A-Deny-Survives-And-An-Answer-Without-The-Secret-Is-Refused]]"
  - "[[TASK-0670-A-Permission-Prompt-Sits-In-The-Needs-You-List-Like-Its-Other-Rows]]"
  - "[[TASK-0677-The-Secret-Leak-Test-Runs-On-Python-3-11-And-3-12]]"
  - "[[TASK-0680-FEAT-0159-Review-Round-1-Fixes]]"
release: ""
acceptance_exception: ""
acceptance: "[[TST-0096-A-Permission-Prompt-Is-Answered-From-The-Needs-You-Card]]"
design: ""
related:
  - "[[ISS-0301-A-Framed-Page-Can-Post-To-The-Loopback-Write-Endpoints]]"
  - "[[FEAT-0156-Claude-Sessions-Report-Through-The-Cockpit-Plugin]]"
  - "[[FEAT-0076]]"
  - "[[FEAT-0079-Supervision-From-A-Phone]]"
  - "[[PHASE-031-The-Supervised-Week]]"
  - "[[RISK-0006-The-Unattended-Worker]]"
  - "[[REQ-0026-Only-Human-Owned-Transitions]]"
  - "[[REQ-0027-Every-Write-Guarded]]"
  - "[[ADR-0009-The-Principal-Is-A-Role]]"
  - "[[FEAT-0158-A-Dispatched-Prompt-Is-Submitted-Not-Typed]]"
  - "[[RISK-0012-A-Local-Request-Can-Put-A-Prompt-Into-A-Claude-Session]]"
  - "[[RISK-0013-Approving-In-The-Cockpit-Runs-A-Command]]"
reviewed_by: ["model:claude-opus-5-5 (independent-reviewer, round 1, A)", "model:claude-opus-5-5 (independent-reviewer, round 1, B)"]
review_date: 2026-10-21
review_verdict: changes-requested
review_round: 1
---

# A permission prompt is answered from the cockpit

**Built on 2026-10-14; its tasks are done** (six since TASK-0670 and TASK-0677) ([[CHG-20261014-A-Permission-Prompt-Is-Answered-From-The-Cockpit]]). It stays `doing` until Edwin walks [[TST-0096-A-Permission-Prompt-Is-Answered-From-The-Needs-You-Card]] after a desktop rebuild and restart, and the independent review approves it. Two things changed while building, both from live runs in a real Claude session: an ask is offered only in manual or acceptEdits mode, because in auto mode every classified call waited 5 s for nothing; and a session's records also close when its main-loop turn ends or the person sends the next prompt, because a refusal in the terminal reports nothing. One question is still Edwin's: whether the card should offer no buttons while the app runs with a Chrome debugging port (plan, "Open question").

*As started:*  Edwin chose to start it after [[FEAT-0158-A-Dispatched-Prompt-Is-Submitted-Not-Typed]] was done, and answered its three open questions (below, "Decisions"). It no longer waits on [[ISS-0301-A-Framed-Page-Can-Post-To-The-Loopback-Write-Endpoints]]: this feature builds the secret that issue's open half asks for, for two routes. The plan is `plan/PLAN.md`, the acceptance check is [[TST-0096-A-Permission-Prompt-Is-Answered-From-The-Needs-You-Card]], and the new hazard is [[RISK-0013-Approving-In-The-Cockpit-Runs-A-Command]].

## Tasks, in order

1. [[TASK-0664-The-Sidecar-Requires-The-Shells-Secret-To-Answer-A-Prompt-Or-Deliver-One]]. The shell makes a secret per sidecar and gives it on standard input; the answer route and the delivery route require it.
2. [[TASK-0665-The-Plugin-Asks-The-Cockpit-Before-The-Terminal-And-Never-Widens-A-Deny]]. The plugin's `tool.check` hook, and the sidecar routes it asks and hands back through.
3. [[TASK-0666-The-Needs-You-Card-Answers-A-Permission-Prompt]]. The card and its buttons, which do not exist yet, answering through the shell's main process.
4. [[TASK-0667-Tests-Prove-A-Deny-Survives-And-An-Answer-Without-The-Secret-Is-Refused]]. The tests for the feature's three promises, each shown to fail without its guard; register rows and the change note.

## Decisions, 2026-10-14

1. **The secret guards two routes.** It is required on `POST /api/cockpit/approve` (the answer) and on `POST /api/cockpit/deliveries` (the route that puts a prompt into a Claude session, [[RISK-0012-A-Local-Request-Can-Put-A-Prompt-Into-A-Claude-Session]]). Not on every write route; the rest stays under ISS-0301. The `cockpit dispatch` command is unaffected: it posts a note ID and a verb to `/api/cockpit/dispatch`, and the shell's main process turns that into a delivery and sends the secret itself.
2. **`agent:principal` may answer a prompt that runs a command.** `approvals.answer` keeps accepting it. **Assumption that follows:** the route still requires the shell's secret, and only the shell's main process holds it and always answers as the person. So a delegated principal can answer only through a path that holds the secret, and this feature builds none. This resolves the tension with [[ADR-0009-The-Principal-Is-A-Role]] that PHASE-046's impact analysis recorded.
3. **The wait is 5 seconds, configurable per workspace.** After it, the plugin returns the original `ask` and the terminal prompt appears as today. The value is `approvalWaitMs` on the workspace's record in the shell's `workspaces.json`; 0 turns cockpit answering off. No settings screen in this feature.

## Acceptance Criteria

Written 2026-10-21, after round 1 of the review found the note had none. They restate the goal, the plan's "What the implementation must not do" and the decisions of 2026-10-14.

1. When Claude Code's own rules, mode and hooks answer `ask` for a tool call in manual or acceptEdits mode, the call appears in the cockpit's Needs you list within a second, naming the project, the agent, the tool and the whole command, with Approve and Deny.
2. Approve or Deny on that row is the session's answer, and the terminal shows no prompt of its own while the row waits.
3. With no click within the workspace's wait (5 s unless set; 0 turns this off), the terminal shows its own prompt as before, and the row says to answer there and offers no buttons.
4. An `allow` or a `deny` from beneath the plugin, a PreToolUse hook's deny among them, is never changed.
5. `POST /api/cockpit/approve` and `POST /api/cockpit/deliveries` refuse a request without the shell's secret. The secret reaches the sidecar on stdin only, never in its arguments, environment, responses or files, and only the shell's main process reads it.
6. An `agent:` actor other than `agent:principal` cannot answer, even with the secret.
7. The answer is recorded as the person's (`user:<name>`), whatever the renderer sends.
8. A program connected to the app's debugging port can answer as the person can; the secret cannot tell them apart. Whether to refuse answers then is open question 1, Edwin's ([[RISK-0013-Approving-In-The-Cockpit-Runs-A-Command]]).

## Review

**Round 1, 2026-10-21: changes-requested.** Two `independent-reviewer` sessions (A and B) worked from the same packet in clean contexts. Both are the same model as the author (`claude-opus-5-5`); independence here is the clean context (ADR-0013).

| # | Claim | Combined verdict | Evidence |
|---|---|---|---|
| 0 | The feature's acceptance criteria | refuted: none existed | Both. Written above, 2026-10-21. |
| 1 | The secret is made per sidecar and passed on stdin only | holds | A: `randomBytes(32)`, `--secret-stdin`, `child.stdin?.end(...)`. B: the leak test searches argv, `ps -E`, four responses, `.cockpit/` and stderr. |
| 2 | `/approve` and `/deliveries` refuse a request without the secret | holds | A: removing the check at each route failed 14 and 5 tests. B: making `_require_shell_secret` pass failed 17. |
| 3 | An `agent:` actor other than `agent:principal` is refused | holds | A: `if False:` failed six cases. B: removing the lower-casing failed two. |
| 4 | The plugin never changes an `allow` or a `deny` from beneath | holds | Both: removing `if (asked.decision !== 'ask') return false` failed "a deny from a PreToolUse hook survives…" and "an allow from beneath is returned as it is". A noted the live-hook test never reaches that line, so only the folded-verdict test guards it. |
| 5 | The wait runs out to the terminal; offered only in manual and acceptEdits; `approvalWaitMs` 0 turns it off | holds (tests and reading) | Both. |
| 6 | The renderer never holds the secret or chooses the actor | holds | Both: `postAnswer` adds the secret, the actor is `personActor()`, and the source scan allows exactly two callers. |
| 7 | Goal: "nobody else can answer it" | refuted while a debugging port is open | A. This was already open question 1; criterion 8 now says it plainly. |
| 8 | TST-0096 guards the behaviour | not checked: step 9 not yet walked | Both. |

**The packet was incomplete.** It left out `1072111` (TASK-0665) and `ba33244` (TASK-0666), which hold the plugin's `tool.check` hook, the ask and hand-back routes and the shell's answer handler. Their subjects name only task IDs, and the packet script read the feature's `tasks:` field only when written on one line. Both reviewers followed their claims into that code. Fixed in the template: project-os-dev TASK-0210.

**Other observations, and what was done:**

- A localhost page opened in a new window might inherit the preload, and with it `window.cockpit` (A, unverified): **does not hold**. Checked on 2026-10-21 in Electron 32.3.3, the app's version, with a window built like the app's (preload, context isolation, the same `setWindowOpenHandler` returning `{ action: 'allow' }`): the main window saw `typeof window.cockpit` = `object`, the popup at `http://127.0.0.1:<port>/x` saw `undefined`.
- `approvals.ask` reused a record by `tool_use_id` without checking the session (A): **fixed**, a record is reused only for the same session and tool call ([[TASK-0680-FEAT-0159-Review-Round-1-Fixes|TASK-0680]]).
- TST-0096 step 1's `ls -la` may not ask at all (B): **fixed**, step 1 now asks for a command that writes a file.
- The opening paragraph said "all four tasks" (A): **fixed**.
- The plugin reads its answer from an unauthenticated `GET`, so a process that can rewrite `hook-env` in the app's own data folder, or answer on the sidecar's port after it exits, could grant asks (B): recorded in [[RISK-0013-Approving-In-The-Cockpit-Runs-A-Command]]. Both need a process running as the same user, which can already type into the terminal.
- `cockpit dispatch` still reaches a session without the secret (A): decided on 2026-10-14 (Decision 1); [[RISK-0012-A-Local-Request-Can-Put-A-Prompt-Into-A-Claude-Session]] stays partly open for it.

## Goal

Today the cockpit shows an amber card when a Claude session asks for permission, but answering still means finding the terminal and typing (`approvals.py`, module docstring). The card is the session's `needs-input` state, set by the `PermissionRequest` hook (`agent_hooks.py`). The approvals store behind the planned buttons exists but is unused: nothing calls `record()` outside `tests/test_approvals.py`, and no client calls `GET /api/cockpit/approvals` or `POST /api/cockpit/approve`. So the buttons and the recording are both built here. After this feature, the card's approve and deny buttons are the answer. The plugin waits a bounded time for the person's click; if none comes, the terminal prompt appears exactly as it does today.

## Findings

- **The hook.** A `tool.check` hook calls `next(e)` first, so Claude Code's own rules and the user's PreToolUse hooks decide before the cockpit is asked. Only when the result is `ask` does the plugin post to the approvals store and wait. `tool.check` fires before the mode settles an ask, so `PermissionRequest` has not fired yet and the plugin must record the approval itself. It returns `allow` or `deny` from the person's answer, or returns the original `ask` when the wait runs out. **It never changes a `deny`.** The mods documentation warns that a mod can approve calls the user's own PreToolUse hooks blocked; this rule is what prevents that, and it needs a test.
- **The wait.** A hook has a 10 s limit, but waiting inside a mods API call such as `$.http.fetch` does not count toward it. The wait should be short, so a person at the terminal is not kept from their own prompt. Edwin chose 5 s on 2026-10-14.
- **Why the answer route is not safe yet.** The answer endpoint (`server.py`, `_serve_approve`, `POST /api/cockpit/approve`) accepts `approval_id`, `decision` and `actor` from the request body, and checks only that the request came from this machine. `approvals.answer` refuses an actor that starts with `agent:`, but the actor is whatever the request says. Today that costs little, because an answer changes only a record. Once an answer approves a Bash call, any loopback POST that claims to be `user:edwin` runs a command. Two ways to send one exist already: a script in a framed HTML page (ISS-0301), and the agent itself, through any tool it is already allowed that can reach localhost.
- **What the secret must be.** A value the shell holds and passes to the sidecar, which the sidecar requires on the answer route. It must not be in any environment variable or file the Claude session can read. Passing it in the sidecar's environment is not enough if a same-user process can read another process's environment; passing it on the sidecar's standard input at spawn avoids that question. The plugin does not need the secret: it reads the answer, it does not write it.
- **Who may answer.** [[REQ-0026-Only-Human-Owned-Transitions]] says the cockpit performs only human-owned transitions. `approvals.answer` lets `agent:principal` answer, because [[ADR-0009-The-Principal-Is-A-Role]] allows a delegation policy to give the principal role to an agent (`delegation.py`). For a record that was harmless. For an answer that runs a command it was an open question; Edwin decided on 2026-10-14 that it may (Decisions, 2).
- **What it unblocks.** [[FEAT-0076]] promises that nothing waits silently without bound, and every mechanism behind that promise watches the review queue. A permission prompt answered through the approvals store is a queue entry, so the stall alarm in [[PHASE-031-The-Supervised-Week]] can see it, which [[RISK-0006-The-Unattended-Worker]] needs. [[FEAT-0079-Supervision-From-A-Phone]] would answer through the same route and needs the same secret.

### Candidate tasks, as filed on 2026-10-08 (minted as TASK-0664 to TASK-0667)

1. The shell's secret, given to the sidecar at spawn and required on the answer route; a request without it is refused. This closes the open half of ISS-0301 for this route.
2. The plugin's `tool.check` hook: `next(e)` first, wait only on `ask`, never change a `deny`, fall back on timeout.
3. The cockpit card's buttons send the answer with the secret; the card says when the wait ran out and the terminal has the prompt.
4. Tests: a PreToolUse `deny` survives a cockpit `allow`; an answer without the secret is refused; an `agent:` actor is refused.

## Open questions

1. **Should a cockpit approval be refused while the app runs with a Chrome debugging port?** Any local program connected to that port can press Approve as you do, and the secret cannot tell the difference ([[RISK-0013-Approving-In-The-Cockpit-Runs-A-Command]]). The app has been started with `--remote-debugging-port=9222` for development. Recommendation: the main process checks for the switch and, when it is set, the card says "Answer in the terminal: the app was started with a debugging port" and offers no buttons. This is not planned in any task; it would be a small addition to TASK-0666 if you want it.

The three questions filed on 2026-10-08 are answered under "Decisions, 2026-10-14".

## Verification

Full run on 2026-10-21, project-os-cockpit 541bba6, after the push and with every later commit from other sessions included:

- `.venv/bin/python -m pytest -q` (Python 3.13): 2254 passed, 10 skipped.
- `node --test tests/*.test.mjs` in `desktop/` after `npm run build`: 229 tests, 229 pass.
- `claude plugin test .` in `desktop/plugin/claude-code` (Claude Code 2.1.303): 62 pass, 0 fail.
- CI on 65c6de9: validate-docs (Python 3.12, Linux) and observed-coverage (Python 3.11, macOS, Claude Code 2.1.300) both green, after TASK-0677 fixed one test that failed before Python 3.13.

## Links

- Phase: [[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]
- Plan: `plan/PLAN.md`
- Acceptance: [[TST-0096-A-Permission-Prompt-Is-Answered-From-The-Needs-You-Card]]
- Risks: [[RISK-0013-Approving-In-The-Cockpit-Runs-A-Command]], [[RISK-0012-A-Local-Request-Can-Put-A-Prompt-Into-A-Claude-Session]]
- Code: `src/project_os_cockpit/approvals.py`, `src/project_os_cockpit/server.py` (`_serve_approve`, `_serve_delivery_add`), `src/project_os_cockpit/__main__.py`, `desktop/src/ipc/sidecar.ts`, `desktop/src/ipc/dispatch-queue.ts`, `desktop/plugin/claude-code/hooks/register.ts`, `desktop/src/renderer/renderer.ts` (Needs you), `src/project_os_cockpit/delegation.py`
