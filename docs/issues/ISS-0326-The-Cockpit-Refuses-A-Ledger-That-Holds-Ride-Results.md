---
type: "[[issue]]"
id: ISS-0326
aliases: ["ISS-0326"]
title: "The cockpit refuses a ledger that holds a ride's results, drops fields it does not know when it rewrites one, and counts owed checks by command: alone"
status: open
phase: ""
owner: user:edwin
created: 2026-10-21
updated: 2026-10-21
source: ["project-os a76657d (project-os-dev TASK-0205 and TASK-0206, CHG-20261021-A-Command-Can-Cover-One-Platform-And-A-Release-Test-Can-Be-Ridden), whose Impact section says: 'project-os-cockpit reads ledgers with its own method list, so it refuses a ride entry and drops build when it rewrites a ledger. It also counts owed checks by command: alone. Both need a cockpit change before a repo imports a ride.'", "your-trainer FEAT-0140, the release ride"]
reported_by: agent
question: ""
severity: high
component: "acceptance"
parent: ""
related: ["[[project-os-dev#ISS-0108]]", "[[project-os-dev#ISS-0109]]"]
tests: []
tasks: ["[[TASK-0678]]"]
---

# The cockpit refuses a ledger that holds a ride's results

## Problem

Once your-trainer imports its first release ride, the cockpit stops showing that repo's acceptance checks and release test. The template's `release-test.py --import-ride` (project-os a76657d) adds ledger entries with `method: "ride"` and a `build` such as `"2.2.0 (123)"`. The cockpit's `ledger.check_entry` accepts only `manual`, `automated` and `migration`, so it raises `LedgerError` on the whole file.

Three smaller gaps sit beside it:

- When the cockpit writes a result into a ledger, `Ledger.to_json` keeps only the fields it knows. It drops each ride entry's `build`, and any other field or top-level key it does not know.
- The template now treats a check as automated on platform P when it has `command:` or `commands.P` (a map keyed by platform). On a covered platform, `hand_steps:` keeps the check owed for those steps only. The cockpit's `acceptance.kind_of` reads `command:` alone. So a check with only `commands: {android: ...}` is owed on Android in the cockpit and not in `release-test.py`, and the release page's owed count disagrees with the sheet.
- Each sheet now prints a hand-run budget line ("37 checks with 240 steps are owed by hand on Android. The limit is 10 checks."), and the cockpit shows nothing like it.

## Expected

The cockpit reads and keeps ride entries, keeps every field it does not know when it rewrites a ledger, counts owed checks the way `release-test.py` does on each platform, and shows the budget line beside the release's owed count.

## Next Actions
- [ ] [[TASK-0678-The-Cockpit-Reads-Ride-Results-And-Counts-Owed-Checks-As-The-Release-Test-Does]]
