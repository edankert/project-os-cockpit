---
type: "[[task]]"
id: TASK-0491
aliases: ["TASK-0491"]
title: "`level:` describes what a test exercises and nothing else — the human-walked population stops being special-cased rather than being moved"
status: done
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

# `level:` describes what a test exercises

*(Re-scoped 2026-08-18. This task was **"tier the twenty-two"** under [[ADR-0033-A-Manual-Test-Is-An-Acceptance-Test]], which said the human-walked notes should become acceptance tests at a tier. [[ADR-0034-Three-Axes-Not-One-Word]] supersedes that: **`level:` does not imply who runs a test**, so a human-walked `level: system` test is not a contradiction and does not need to move anywhere. What moves is the machinery, not the notes.)*

**The population is 30, not 22** — measured with the reader's predicate rather than by looking for the word *manual*: 5 here, 18 in `your-trainer` (3 of them now `retired`), 7 in `your-health`. The 22 figure counted only notes carrying `kind: manual` explicitly, which is the weaker rule this phase is deleting.

**Nothing is re-tiered and nothing is re-homed.** A test at `level: system` with no `command:` is exactly what it says: a system-level test a person runs. It stays where it is, keeps its level, and stops being treated as a different kind of thing. The tier system belongs to the release checklist and, under [[ADR-0034]] decision 6, survives only if it earns its place as a **lifetime** field.

The original framing, kept because the reversal is the point:

- **Tier 1** — a capability that will still be true next year (`TST-0024` Remote SSH walk).
- **Tier 2** — a regression guard, which must name the `ISS-*` it guards.
- **Tier 3** — a one-build verification. **This is the find**: `TST-0026` asserts a measured *"64 to 31"* claim that would give different numbers on any later day, and TESTING.md already says Tier 3 is removed or promoted after a verified release. The genuinely transient case has a home and it is not a separate type.

**`TST-0011` is not one note's worth of work.** It is a 13-item checklist whose items already exist as separate acceptance tests — item 7 is `TST-0065` *The fleet view* and `TST-0064` *A session is visible while it runs*. Splitting it is how [[ISS-0195-Two-Types-Carry-One-Act]]'s duplicate resolves; folding it in whole would preserve the duplicate inside the tier system.

Done when: no note carries the combination, every migrated note names its tier's justification, and the duplicate is gone rather than moved.

## Done 2026-08-18

**Nothing was tiered and nothing was moved**, which is the re-scope rather than a shortcut: under [[ADR-0034-Three-Axes-Not-One-Word]] a human-walked `level: system` test is not a contradiction. What changed is that the machinery stopped keying on it.

**The population is 30, not 22** — measured with the reader's predicate rather than by looking for the word *manual*: 5 here, 18 in `your-trainer`, 7 in `your-health`. The 22 came from counting `kind: manual` explicitly, which is the weaker rule this phase deleted.
