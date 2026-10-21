---
type: "[[task]]"
id: TASK-0680
aliases: ["TASK-0680"]
title: "FEAT-0159 review round 1: an ask reuses a record only for the same session and tool call, TST-0096 step 1 asks for a command that writes, and RISK-0013 names the unauthenticated read"
status: done
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-21
updated: 2026-10-21
source: ["[[FEAT-0159-A-Permission-Prompt-Is-Answered-From-The-Cockpit]], '## Review', round 1"]
parent: "[[FEAT-0159-A-Permission-Prompt-Is-Answered-From-The-Cockpit]]"
effort: "XS"
due: ""
depends: []
blocks: []
related: ["[[TST-0096-A-Permission-Prompt-Is-Answered-From-The-Needs-You-Card]]", "[[RISK-0013-Approving-In-The-Cockpit-Runs-A-Command]]"]
tests: []
---

# FEAT-0159 review round 1 fixes

Round 1 of FEAT-0159's independent review found these in code and notes the feature changed. Each is fixed here, and round 2 checks them.

## Definition of Done

- [x] `approvals.ask` reuses an existing record only when both the session and the `tool_use_id` match. A test registers the same `tool_use_id` from two sessions and gets two records; it fails with the old match.
- [x] TST-0096 step 1 asks Claude to create a file with Bash, which asks in manual mode, instead of `ls -la`, which may be allowed without asking.
- [x] RISK-0013 names the plugin's unauthenticated `GET` of its answer: a process running as the same user that rewrites `hook-env`, or answers on the sidecar's port after it exits, could grant an ask.
- [x] The approval tests pass.

## Result

- `ApprovalStore.ask` reuses a record only when `tool_use_id` and `session_id` both match. `test_another_sessions_offer_with_the_same_call_id_gets_its_own_record` fails with the old match (1 failed, 12 passed) and passes with the new one. The approval tests pass (39).
- TST-0096 step 1 and its expectations use `touch /tmp/tst-0096-step1.txt`.
- RISK-0013, "What the secret does not stop", names the plugin's unauthenticated read of its answer.
