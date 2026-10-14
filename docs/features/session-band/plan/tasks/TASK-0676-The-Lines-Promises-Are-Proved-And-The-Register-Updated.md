---
type: "[[task]]"
id: TASK-0676
aliases: ["TASK-0676"]
title: "FEAT-0157's promises are proved with tests that fail when their guard is removed, the register and RISK-0004 are current, the change note is written, and TST-0097 is ready to walk"
status: done
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[FEAT-0157-The-Project-State-Sits-Above-The-Claude-Prompt]]"]
parent: "[[FEAT-0157-The-Project-State-Sits-Above-The-Claude-Prompt]]"
effort: "S"
due: ""
depends: ["[[TASK-0673-The-Cockpits-Facts-Join-The-End-Of-The-Project-Line]]", "[[TASK-0674-Open-In-Cockpit-Brings-The-Cockpit-Forward-On-The-Focus-Item]]", "[[TASK-0675-Cockpit-Needs-And-Cockpit-Release-Answer-In-A-Pane-Without-A-Turn]]"]
blocks: []
related: ["[[TST-0097-The-Cockpits-Counts-And-Open-Button-Sit-On-The-Project-Line]]", "[[RISK-0004-Hook-Injection-Surface]]"]
tests: []
---

# The line's promises are proved and the register updated

## Definition of Done

- [x] Each promise in plan/PLAN.md "What the implementation must not do" has a test, and each test is shown to fail with its guard removed: no other-projects count of 0; no count from a stale or missing file; no own line drawn when the project-os line is there; no turn started by either command; `open` never given a value that failed its pattern.
- [x] A sweep shows nothing new written under `~/.claude` during a session with the line (RISK-0004's existing check, run again).
- [x] [[RISK-0004-Hook-Injection-Surface]] names `needs-elsewhere.json` beside `hook-env`.
- [x] Every row in plan/PLAN.md "Capability register" is in `docs/reference/cockpit-capability-register.md`, each in the same commit as its change note.
- [x] A change note, `docs/changes/CHG-20261014-The-Cockpits-Facts-Join-The-Project-Line.md` (or the date it lands), with its Impact list naming the Claude terminal.
- [x] [[TST-0097-The-Cockpits-Counts-And-Open-Button-Sit-On-The-Project-Line|TST-0097]]'s steps match what was built.
- [x] PHASE-046's exit criterion for the line is ticked or says what is left.

## Steps

- [x] Guarantee tests with mutations.
- [x] RISK-0004, register, change note, TST-0097.

## Result (2026-10-14)

- **Guarantees.** Each promise in the plan's "What the implementation must not do" has a test. Each was shown to fail with its guard removed, here or in the task that built it: a sum of zero and a missing or stale file draw no other-projects count (`line.test.ts`, the two-minute check mutated); the cockpit draws no line of its own when project-os's is there (one `segment:cockpit`, inside the line; the join mutated); neither command returns text or submits a prompt (text returned, mutated); `open` never gets a value that failed its pattern (the workspace check removed, mutated). Two cases were added here: no file, and exactly one segment.
- **`~/.claude`.** RISK-0004's verification test, `claude-plugin-shell.test.mjs`, passes in the node suite. The cockpit writes nothing new there. Claude Code now records the project-os marketplace there on its own, and RISK-0004 says so.
- **The full suite**: 2,238 passed, 11 skipped, node suite included. It first failed in `test_remote_peer_refusal.py`: TASK-0672's route is a deliberate 39th loopback guard, and the count there is raised with a dated comment.
- RISK-0004, the register, [[CHG-20261014-The-Cockpits-Facts-Join-The-Project-Line]], TST-0097 (step 7 narrowed to what the pane shows; step 10 added for a narrow band) and PHASE-046 are updated.
