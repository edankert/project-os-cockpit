---
type: "[[task]]"
id: TASK-0432
aliases: ["TASK-0432"]
title: "The gate lists its checks — the 60 by name, each reaching its own section, and the stated number equals the rows listed"
status: done
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["Edwin 2026-08-16: 'I still don't seem to be able to SEE … the current set'"]
parent: "[[FEAT-0103-The-Gate-Is-Walkable]]"
effort: M
depends: ["[[TASK-0430-The-Suite-Is-Addressable]]", "[[TASK-0431-Declare-The-Next-Release]]"]
blocks: ["[[TASK-0433-The-Acceptance-Walker]]"]
related: ["[[ADR-0028-Work-Has-Three-Phases]]"]
tests: ["[[TST-0029-The-Walker-Ticks-What-It-Walked]]"]
---

# The gate lists its checks

## What

The gate group renders 17 rows that are **area names with counts**. It renders the 60 **checks** instead, grouped by area, each carrying its number and name and linking to its own section anchor.

The anchors already exist in the rendered document (`#125-trainer-compatibility-verification`); nothing uses them. Today every row opens the file at the top, and section 1.25 starts at line 522 of 1082 after 327 other checkboxes.

## The thing this must not undo

**One obligation, never sixty** ([[ADR-0028]]). Listing the checks is a rendering decision; it must not put 60 back on any badge. `TST-0028`'s bound assertion stays as written, and this task is done only with it still passing.

## Definition of done

- [ ] The gate lists the individual gating checks, grouped by area, ordered by section
- [ ] The number the group states equals the number of rows it lists — one computation, not two
- [ ] A row links to its own section anchor and lands there
- [ ] A row names its check (`1.25.3 · ERG holds target watts`), not just its area
- [ ] Tier 3 is listed where present and marked as non-gating
- [ ] A `- [~]` reconciled row renders as reconciled, never as walked or as owed
- [ ] The badge is unchanged: still one obligation while a release is `draft`, zero otherwise
