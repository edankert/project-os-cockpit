---
type: "[[task]]"
id: TASK-0676
aliases: ["TASK-0676"]
title: "FEAT-0157's promises are proved with tests that fail when their guard is removed, the register and RISK-0004 are current, the change note is written, and TST-0097 is ready to walk"
status: backlog
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

- [ ] Each promise in plan/PLAN.md "What the implementation must not do" has a test, and each test is shown to fail with its guard removed: no other-projects count of 0; no count from a stale or missing file; no own line drawn when the project-os line is there; no turn started by either command; `open` never given a value that failed its pattern.
- [ ] A sweep shows nothing new written under `~/.claude` during a session with the line (RISK-0004's existing check, run again).
- [ ] [[RISK-0004-Hook-Injection-Surface]] names `needs-elsewhere.json` beside `hook-env`.
- [ ] Every row in plan/PLAN.md "Capability register" is in `docs/reference/cockpit-capability-register.md`, each in the same commit as its change note.
- [ ] A change note, `docs/changes/CHG-20261014-The-Cockpits-Facts-Join-The-Project-Line.md` (or the date it lands), with its Impact list naming the Claude terminal.
- [ ] [[TST-0097-The-Cockpits-Counts-And-Open-Button-Sit-On-The-Project-Line|TST-0097]]'s steps match what was built.
- [ ] PHASE-046's exit criterion for the line is ticked or says what is left.

## Steps

- [ ] Guarantee tests with mutations.
- [ ] RISK-0004, register, change note, TST-0097.
