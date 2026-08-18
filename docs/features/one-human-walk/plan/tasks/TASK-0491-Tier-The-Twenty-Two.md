---
type: "[[task]]"
id: TASK-0491
aliases: ["TASK-0491"]
title: "Tier the twenty-two — a judgement per note, not a bulk rewrite"
status: backlog
phase: "[[PHASE-036-One-Human-Walk]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
source: ["[[FEAT-0122-One-Human-Walked-Population]]"]
parent: "[[FEAT-0122-One-Human-Walked-Population]]"
effort: M
depends: []
blocks: []
related: []
tests: []
---

# Tier the twenty-two

22 notes fleet-wide carry `kind: manual` outside `level: acceptance`: **5 here, 15 in `your-trainer`, 2 in `your-health`**. Each becomes an acceptance test at a tier, and the tier is a reading rather than a default:

- **Tier 1** — a capability that will still be true next year (`TST-0024` Remote SSH walk).
- **Tier 2** — a regression guard, which must name the `ISS-*` it guards.
- **Tier 3** — a one-build verification. **This is the find**: `TST-0026` asserts a measured *"64 to 31"* claim that would give different numbers on any later day, and TESTING.md already says Tier 3 is removed or promoted after a verified release. The genuinely transient case has a home and it is not a separate type.

**`TST-0011` is not one note's worth of work.** It is a 13-item checklist whose items already exist as separate acceptance tests — item 7 is `TST-0065` *The fleet view* and `TST-0064` *A session is visible while it runs*. Splitting it is how [[ISS-0195-Two-Types-Carry-One-Act]]'s duplicate resolves; folding it in whole would preserve the duplicate inside the tier system.

Done when: no note carries the combination, every migrated note names its tier's justification, and the duplicate is gone rather than moved.
