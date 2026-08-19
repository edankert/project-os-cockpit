---
type: "[[task]]"
id: TASK-0562
aliases: ["TASK-0562"]
title: "Strip the verdict from the 49 automated notes that carry one"
status: backlog
phase: "[[PHASE-039-A-Test-Says-Who-Executes-It]]"
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
source: []
parent: "[[FEAT-0139-The-Suite-Is-The-Verdict]]"
effort: "M"
due: ""
depends: ["[[TASK-0559-The-Runner-Reports-And-Does-Not-Write]]"]
blocks: []
related: []
tests: []
---

# Strip the verdict from the 49 automated notes that carry one

## Definition of Done
- [ ] No automated note holds `passing`/`failing`, `last_run:` or `exit_code:`
- [ ] Counts recorded per repo before and after
- [ ] The 65 manual verdict-bearing notes are untouched, asserted by count

## Steps
- [ ] This repo first: 37 verdicts, 38 `last_run`, 29 `exit_code`
- [ ] Then `your-health` 6, `project-os-dev` 4, `your-trainer` 2 — and your-trainer's 69 orphan `exit_code` values
- [ ] Set `status:` to `active` unless the note is `retired`

## Notes

Measured 2026-08-19: 139 automated notes carry 49 verdicts, 50 `last_run`, **108 `exit_code`**. `your-trainer` holds 69 exit codes against 2 verdicts — residue of a runner writing a value the validator forbids.

**Do not sweep `your-trainer` blind**: it carries other people's in-flight work.
