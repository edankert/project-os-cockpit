---
type: "[[task]]"
id: TASK-0667
aliases: ["TASK-0667"]
title: "Tests prove a PreToolUse deny survives a cockpit approval, an answer without the secret is refused, and an agent other than the principal cannot answer; register rows and the change note"
status: backlog
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

- [ ] **A PreToolUse deny survives a cockpit approval.** A `claude plugin test` case with a user PreToolUse hook that denies a Bash call, and a stand-in sidecar that answers `granted` to every approval at once. The call is refused, and the sidecar received no `ask`. With the hook's `next(e)` check removed, the test fails.
- [ ] **An answer without the secret is refused.** A pytest sweep over both guarded routes with no header, an empty header, a wrong secret and the right secret with one character changed: all 403, and the approval or delivery is unchanged. With the check removed from either route, it fails.
- [ ] **An `agent:` actor other than the principal is refused**, even with the secret: `agent:claude`, `agent:codex`, `Agent:Worker`. `agent:principal` with the secret is accepted (Edwin, 2026-10-14). With the rule removed from `approvals.answer`, the test fails.
- [ ] **The secret does not leak.** A test that starts a sidecar the way the shell does and searches the sidecar's argv and environment, `.cockpit/`, the instrument directory including `hook-env`, a new terminal's environment, stderr, and the bodies of `/api/cockpit/state` and `/api/cockpit/approvals` for the secret, and finds it nowhere.
- [ ] Each "fails when removed" run is recorded in this note with its counts.
- [ ] Rows in `docs/reference/cockpit-capability-register.md`: the approval routes (`api.read.approvals`, `api.write.approvals`, or the existing row names), the card's Approve and Deny, and a line that `POST /api/cockpit/approve` and `POST /api/cockpit/deliveries` require the shell's secret.
- [ ] A change note, `docs/changes/CHG-<date>-A-Permission-Prompt-Is-Answered-From-The-Cockpit.md`.
- [ ] [[RISK-0013-Approving-In-The-Cockpit-Runs-A-Command]] and [[RISK-0012-A-Local-Request-Can-Put-A-Prompt-Into-A-Claude-Session]] name the tasks that mitigate them.
- [ ] The full suites pass: `python3 -m pytest -q`, the desktop node tests, `claude plugin validate` and `claude plugin test`.

## Steps

- [ ] The four tests, each run with its guard removed.
- [ ] Register, change note, risks.
- [ ] Full suites.

## Notes

The deny test is the one PHASE-046's exit criteria name. It must use a real PreToolUse hook of the user's kind, not a stub of `next(e)`, or it tests the plugin's reading of the declarations rather than Claude Code's behaviour.
