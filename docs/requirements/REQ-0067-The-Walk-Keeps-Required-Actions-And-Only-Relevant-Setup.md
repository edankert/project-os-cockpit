---
type: "[[requirement]]"
id: REQ-0067
title: "The walk keeps required actions and asks for only relevant setup"
status: approved
phase: ""
owner: user:edwin
created: 2026-09-24
updated: 2026-09-24
source: ["Your Trainer REQ-0209, moved here 2026-09-24. Edwin: 'Make the changes as suggested. move them to the cockpit as suggested.'"]
priority: high
scope: "Release walk page in any project-os workspace, reading the shared walk generator (project-os-dev FEAT-0033)"
acceptance: ["Required preparation is retained without a verdict for settled checks", "Only setup needed by owed observations and their prerequisites is shown", "Invalid dependencies and contradictory state remain visible without losing owed checks", "Platform instructions and fallback remain complete"]
implements: "[[FEAT-0151-The-Release-Walk-Has-One-Next-Action]]"
verifies: []
related: ["[[TASK-0629-Show-One-Walk-Action-And-Its-Readiness]]", "[[REQ-0066-The-Release-Walk-Keeps-Observation-Context]]"]
tests: []
---

# The walk keeps required actions and asks for only relevant setup

## Statement

The generated walk must include every action needed to reach an owed observation, show only the relevant setup and preserve all owed checks when a prerequisite is invalid or unavailable.

## Where this came from

Your Trainer wrote this requirement as REQ-0209 on 2026-09-16, under its FEAT-0122. It describes how the walk page behaves in any project-os workspace, so it moved here on 2026-09-24. Your Trainer's REQ-0209 is now `superseded` and points here. The generator's side of this requirement is built in project-os-dev FEAT-0033 and TASK-0125. This repository owns showing its result: the page keeps each preparation action, the relevant setup and each readiness problem visible, and it never drops an owed check.

The letters in the evidence column (A1, B5 and so on) are the detailed criteria in [[FEAT-0151-The-Release-Walk-Has-One-Next-Action]].

## Acceptance Criteria

- [x] Required preparation is retained without a verdict for settled checks — evidence: FEAT-0151 detailed criteria A1 and A4 are met. The generator retains the actions, and the page shows them with Continue and no verdict. The tests are listed under "Implementation evidence, 2026-09-16" in Your Trainer FEAT-0122.
- [ ] Only setup needed by owed observations and their prerequisites is shown — evidence: A2 is met. A3 waits on the Your Trainer procedure audit (Your Trainer TASK-0960).
- [ ] Invalid dependencies and contradictory state remain visible without losing owed checks — evidence: A4 is met. A5 and A6 are open: the page shows declared readiness, and the procedures still need declarations (Your Trainer TASK-0960).
- [ ] Platform instructions and fallback remain complete — evidence: D1 is met. A8 is open until the Your Trainer platform audit is done.

A criterion is ticked only when every letter it names is met.

## Traceability

- Implements: [[FEAT-0151-The-Release-Walk-Has-One-Next-Action]].
- Overlaps: [[REQ-0066-The-Release-Walk-Keeps-Observation-Context]], this feature's first requirement, which states the same goal in four lines.
