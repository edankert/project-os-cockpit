---
type: "[[task]]"
id: TASK-0425
aliases: ["TASK-0425"]
title: "The quiet is on screen — what the in-flight rule silenced collapses into a line that says how many and why, and opens in one click"
status: done
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["[[ADR-0028]] decision 5", "Edwin's original report: what needs a person is invisible — derived silence that cannot be opened is the same failure inverted"]
parent: "[[FEAT-0101-Obligations-Route-By-The-State-Of-Their-Subject]]"
effort: S
depends: ["[[TASK-0424-The-In-Flight-Predicate]]"]
blocks: []
related: ["[[FEAT-0094]]", "[[ADR-0025-An-Owed-Row-May-Appear-Twice]]"]
tests: ["[[TST-0025-Obligation-Routing-Is-Per-Item-And-Complete]]"]
---

# The quiet is on screen

## What

[[TASK-0424]] removes 33 rows from `your-trainer`'s attention surface. This makes those 33 visible as a collapsed line beneath `Needs you`, grouped by phase where the subjects have one:

```
Needs you · 3
  ⌄ 21 more · PHASE-999 Future     (no feature in flight)
     1 more · PHASE-015, PHASE-018
```

Phase is used **only** as the grouping label. The rule reads feature status ([[TASK-0424]]), and a repo with no phases groups by something else or not at all rather than rendering an empty label.

## Why this is not optional

Edwin's report is that owed work is invisible. A change that answers it by making 33 rows disappear with no trace has produced the same failure with the opposite sign — and this project has been bitten by the neighbouring version twice already, where a permanent count taught the reader to stop looking.

The reader must be able to see what the rule decided, and disagree with it in one click.

## Definition of done

- [ ] Every row the in-flight rule suppresses is reachable from a collapsed line under `Needs you` in the view that would have carried it
- [ ] The line states the count and the reason (`no feature in flight`), not just a number
- [ ] Grouped by phase where the subjects name one; a repo with no `PHASE-*` notes renders the line without an empty or invented label
- [ ] Expanding shows the rows with their subject and its status, so the reader can see *why* each is quiet
- [ ] The line is **absent at zero** — this project's standing rule about zero, and a permanent `0 more` is exactly the shape a reader learns to stop seeing
- [ ] The count on the line and the number of rows it expands to come from one computation, not two
- [ ] The suppressed rows do **not** appear in the badge, the digest, or the fleet card. This line is the only place they are counted, and it counts them as suppressed rather than as owed
