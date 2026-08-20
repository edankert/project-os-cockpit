---
type: "[[task]]"
id: TASK-0571
aliases: ["TASK-0571"]
title: "Measure the gate delta per repo before it lands"
status: done
phase: "[[PHASE-039-A-Test-Says-Who-Executes-It]]"
owner: user:edwin
created: 2026-08-19
updated: "2026-08-20"
source: []
parent: "[[FEAT-0140-Sections-Are-Derived-Not-Filed]]"
effort: "M"
due: ""
depends: []
blocks: []
related: []
tests: []
---

# Measure the gate delta per repo before it lands

## Definition of Done
- [ ] Open-check counts recorded per repo, before and after
- [ ] `your-trainer` 68 to 59; this repo and `your-sudoku` unchanged
- [ ] Any repo whose delta differs from the prediction stops the landing

## Steps
- [ ] Record the baseline across every reachable repo
- [ ] Apply, re-measure, and diff against the prediction
- [ ] Write the numbers into the close-out, not just the terminal

## Notes

**This is the only task that changes what a release is allowed to do.** Nine of `your-trainer`'s 68 blocking checks are automated — 4 in Tier 1, 5 in Tier 2.

Every [[PHASE-038]] gate change was measured this way, and the habit exists because a defect invisible in this repo can be live in `your-trainer` ([[ISS-0219]], [[ISS-0221]], [[ISS-0235]]).
