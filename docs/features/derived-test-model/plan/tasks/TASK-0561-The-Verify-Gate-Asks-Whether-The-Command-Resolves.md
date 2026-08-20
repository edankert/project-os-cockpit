---
type: "[[task]]"
id: TASK-0561
aliases: ["TASK-0561"]
title: "The `VERIFY` gate is discharged for an automated test by its command resolving"
status: done
phase: "[[PHASE-039-A-Test-Says-Who-Executes-It]]"
owner: user:edwin
created: 2026-08-19
updated: "2026-08-20"
source: []
parent: "[[FEAT-0139-The-Suite-Is-The-Verdict]]"
effort: "M"
due: ""
depends: ["[[TASK-0566-Resolve-A-Command-And-The-Broken-Command-Section]]"]
blocks: []
related: []
tests: []
---

# The `VERIFY` gate is discharged for an automated test by its command resolving

## Definition of Done
- [ ] An item may reach a terminal status against an automated test whose command resolves
- [ ] It may not when the command does not resolve
- [ ] The manual path is unchanged: `passing`, and not stale

## Steps
- [ ] Branch `validate_docs_bundled.py:2141` on `command:` before reading `status`
- [ ] Reuse [[TASK-0566]]'s resolver — a second implementation is how the two come to disagree
- [ ] Assert the manual branch is untouched by counting gate outcomes before and after

## Notes

This is the clause that makes [[REQ-0058]] safe: removing the verdict without moving the gate would leave every automated test discharging nothing.
