---
type: "[[task]]"
id: TASK-0575
aliases: ["TASK-0575"]
title: "Sync the fleet"
status: backlog
phase: "[[PHASE-039-A-Test-Says-Who-Executes-It]]"
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
source: []
parent: "[[FEAT-0141-The-Contract-Says-It-Upstream]]"
effort: "S"
due: ""
depends: ["[[TASK-0573-Testing-Md-Five-Edits-Upstream]]"]
blocks: []
related: []
tests: []
---

# Sync the fleet

## Definition of Done
- [ ] Every repo carrying an acceptance suite is byte-identical to upstream afterwards
- [ ] `your-health` and `project-os-dev` are no longer stale

## Steps
- [ ] Run the sync per repo
- [ ] Do not stage unrelated dirty files — `your-trainer` carries in-flight work

## Notes

Measured 2026-08-19: this repo, `your-trainer` and `your-sudoku` are byte-identical to upstream. `your-health` and `project-os-dev` are stale by the same 26 lines — a plain sync, no conflict.
