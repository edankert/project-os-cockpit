---
type: "[[feature]]"
id: FEAT-0139
aliases: ["FEAT-0139"]
title: "The suite is the verdict — an automated test stops carrying one, and the gate asks whether its command resolves"
status: done
phase: "[[PHASE-039-A-Test-Says-Who-Executes-It]]"
owner: user:edwin
created: 2026-08-19
updated: "2026-08-20"
source: ["[[ADR-0038-The-Suite-Is-The-Verdict]]"]
goal: "A test note declaring a `command:` records that a machine executes it and nothing about whether it passed; the VERIFY gate is discharged by the command resolving."
requirements: ["[[REQ-0058-An-Automated-Test-Carries-No-Verdict]]"]
tasks: ["[[TASK-0559-The-Runner-Reports-And-Does-Not-Write]]", "[[TASK-0560-The-Forbidden-Status-Check-Widens]]", "[[TASK-0561-The-Verify-Gate-Asks-Whether-The-Command-Resolves]]", "[[TASK-0562-Strip-The-Verdict-From-Forty-Nine-Notes]]", "[[TASK-0563-The-Test-Run-Actuator-Reports]]", "[[TASK-0564-Correct-The-Two-Documents-That-State-The-Reverse]]"]
release: ""
acceptance: ""
design: ""
related: ["[[ADR-0038-The-Suite-Is-The-Verdict]]", "[[project-os-dev#ADR-0010]]", "[[ISS-0239-The-Runner-Stamps-Failing-On-A-Missing-Device]]", "[[ISS-0209-The-Acceptance-Gate-Reaches-No-Fleet-Repo]]"]
tags: [feature, testing]
---

# The suite is the verdict

## Goal

`status: passing` on a note a machine executes is a claim CI already answers, and answers better — it cannot notice a renamed test, and a `command:` that stops resolving can. This feature removes the claim and moves the gate onto the thing that self-corrects.

## Scope

- `run-tests.py` reports and stops writing.
- The forbidden-status rule widens from `level: acceptance` to every note carrying a `command:` — 89 notes to 139.
- The `VERIFY` gate is discharged for an automated test by its command resolving.
- 49 notes are stripped of a verdict they should not hold.

## Out of Scope

- Manual tests. All 65 that genuinely record a human verdict keep `status:` and its staleness clock, untouched.
- The 582 ledger-tracked acceptance checks, whose verdicts [[ADR-0037]] already moved.

## Acceptance

- [ ] `run-tests.py --write` changes no note's `status:`, `last_run:` or `exit_code:`
- [ ] A note with a `command:` holding `passing` is a validator **error**
- [ ] A feature reaching `done` against an automated test is gated on the command resolving, not on a stamped status
- [ ] The 49 stamped notes carry no verdict, per repo, measured before and after
