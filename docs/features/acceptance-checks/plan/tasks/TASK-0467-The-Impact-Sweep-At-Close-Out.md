---
type: "[[task]]"
id: TASK-0467
aliases: ["TASK-0467"]
title: "The impact sweep at close-out — a4577c01's shape, reproduced by tooling: N additions, M invalidations, one Save, one commit"
status: backlog
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
source: ["[[FEAT-0115-The-Sweep-Is-Continuous]]"]
parent: "[[FEAT-0115-The-Sweep-Is-Continuous]]"
effort: L
depends: ["[[TASK-0466-Verdict-Writes-On-Notes]]"]
blocks: []
related: []
tests: []
---

# The impact sweep at close-out

The benchmark is the corpus's own hand commit — `a4577c01`, *"cover TASK-0383..0387 + uncheck overlapping rows"*: six checks added, three invalidated, one commit. The sweep panel reproduces that atomicity with tooling: scoped to a feature reaching `done`, it shows the checks in the areas the feature touched, offers Needs-re-run in place, and takes new checks as repeating rows — name, tier, area inherited, `covers:` prefilled from the feature. **One Save writes N notes + M edits and one commit.** The marginal cost of a new check is a line in a form — the same keystroke count as the line in the file used to be, which is the regression the review said tooling had to prevent.

Closing the sweep writes one line to the feature: `acceptance_impact: <date>`, or `acceptance_impact: none — <reason>`. The feature authors that the sweep happened; the checks author what it did. Neither restates the other.

## Done when

- [ ] A close-out sweep on a real feature produces one commit whose diff is N new notes + M mark clears with reasons — measured against the benchmark's shape.
- [ ] The feature's `acceptance_impact:` line is written by the same Save, never separately.
- [ ] Cancelling writes nothing anywhere.
