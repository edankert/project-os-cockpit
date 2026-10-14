---
type: "[[task]]"
id: TASK-0667
aliases: ["TASK-0667"]
title: "Tests prove a PreToolUse deny survives a cockpit approval, an answer without the secret is refused, and an agent other than the principal cannot answer; register rows and the change note"
status: done
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[FEAT-0159-A-Permission-Prompt-Is-Answered-From-The-Cockpit]], candidate task 4", "plan/PLAN.md, 'What the implementation must not do'"]
parent: "[[FEAT-0159-A-Permission-Prompt-Is-Answered-From-The-Cockpit]]"
effort: "M"
due: ""
depends: ["[[TASK-0666-The-Needs-You-Card-Answers-A-Permission-Prompt]]"]
blocks: []
related: ["[[TST-0096-A-Permission-Prompt-Is-Answered-From-The-Needs-You-Card]]", "[[RISK-0013-Approving-In-The-Cockpit-Runs-A-Command]]", "[[RISK-0012-A-Local-Request-Can-Put-A-Prompt-Into-A-Claude-Session]]"]
tests: ["[[TST-0096-A-Permission-Prompt-Is-Answered-From-The-Needs-You-Card]]"]
---

# Tests prove the feature's three promises

Each earlier task carries unit tests for what it builds. This task holds the tests for the promises the feature makes as a whole, and shows that each one fails when its guard is removed. It also writes the capability register rows and the change note, and gets TST-0096 ready for Edwin.

## Definition of Done

- [x] **A PreToolUse deny survives a cockpit approval.** A `claude plugin test` case with a user PreToolUse hook that denies a Bash call, and a stand-in sidecar that answers `granted` to every approval at once. The call is refused, and the sidecar received no `ask`. With the hook's `next(e)` check removed, the test fails.
- [x] **An answer without the secret is refused.** A pytest sweep over both guarded routes with no header, an empty header, a wrong secret and the right secret with one character changed: all 403, and the approval or delivery is unchanged. With the check removed from either route, it fails.
- [x] **An `agent:` actor other than the principal is refused**, even with the secret: `agent:claude`, `agent:codex`, `Agent:Worker`. `agent:principal` with the secret is accepted (Edwin, 2026-10-14). With the rule removed from `approvals.answer`, the test fails.
- [x] **The secret does not leak.** A test that starts a sidecar the way the shell does and searches the sidecar's argv and environment, `.cockpit/`, the instrument directory including `hook-env`, a new terminal's environment, stderr, and the bodies of `/api/cockpit/state` and `/api/cockpit/approvals` for the secret, and finds it nowhere.
- [x] Each "fails when removed" run is recorded in this note with its counts.
- [x] Rows in `docs/reference/cockpit-capability-register.md`: the approval routes (`api.read.approvals`, `api.write.approvals`, or the existing row names), the card's Approve and Deny, and a line that `POST /api/cockpit/approve` and `POST /api/cockpit/deliveries` require the shell's secret.
- [x] A change note, `docs/changes/CHG-<date>-A-Permission-Prompt-Is-Answered-From-The-Cockpit.md`.
- [x] [[RISK-0013-Approving-In-The-Cockpit-Runs-A-Command]] and [[RISK-0012-A-Local-Request-Can-Put-A-Prompt-Into-A-Claude-Session]] name the tasks that mitigate them.
- [x] The full suites pass: `python3 -m pytest -q`, the desktop node tests, `claude plugin validate` and `claude plugin test`.

## Steps

- [x] The four tests, each run with its guard removed.
- [x] Register, change note, risks.
- [x] Full suites.

## Notes

The deny test is the one PHASE-046's exit criteria name. It must use a real PreToolUse hook of the user's kind, not a stub of `next(e)`, or it tests the plugin's reading of the declarations rather than Claude Code's behaviour.

## Built, 2026-10-14

**The deny, two ways.** In `claude plugin test`, a real classic PreToolUse hook raised by `$.tool.call` ends the call before `tool.check` is raised at all (a probe showed the harness never raises `tool.check` from `$.tool.call`), so the plugin is never asked. That test (`a deny from the person's own PreToolUse hook`) shows the outcome: refused, nothing offered, while the stand-in grants everything. It cannot fail when the plugin's own check is removed, because the plugin is not reached. The test that can is `a deny from a PreToolUse hook survives a cockpit that would grant`, where Claude Code reports the deny through `tool.check` as the declarations describe; with `if (asked.decision !== 'ask') return false` removed, 2 tests fail. **And in the real engine:** a session started with `--settings` pointing at a scratch file whose PreToolUse hook denies `probe-hookdeny`, a stand-in server, and a script granting every open approval each 100 ms. The command did not run, Claude reported "blocked by a test PreToolUse hook", and the server received no `approvals/ask`. Nothing under `~/.claude` was written.

**The pytest promises**, `tests/test_answerable_approval_promises.py`, 17 cases: five wrong secrets (none, empty, wrong, one character off, upper case) on each of the two routes; four agent actors refused with the secret; `agent:principal` accepted; a server started as the shell starts it, with the secret then searched for in its argv, its environment (`ps -E`), `.cockpit/`, its stderr, and four responses; and only `approvals.ts` and `dispatch-queue.ts` calling `sidecarSecretFor`, with the instrument and terminal modules, the renderer and the plugin never naming it.

**Guards removed, one at a time:**

| guard removed | result |
| --- | --- |
| the secret check on `POST /api/cockpit/approve` | 5 failed, 12 passed |
| the secret check on `POST /api/cockpit/deliveries` | 5 failed, 12 passed |
| the `agent:` rule in `approvals.answer` | 4 failed, 13 passed |
| the plugin's `asked.decision !== 'ask'` check | 2 failed (plugin suite) |

**Also:** register rows (`shell.agents.permission-answer` new; four rows dated), [[CHG-20261014-A-Permission-Prompt-Is-Answered-From-The-Cockpit]], both risks naming their tasks, and TST-0096 corrected for manual mode and for what a refusal in the terminal does to the card.
