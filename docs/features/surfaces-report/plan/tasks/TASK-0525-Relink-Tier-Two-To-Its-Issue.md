---
type: "[[task]]"
id: TASK-0525
aliases: ["TASK-0525"]
title: "Restore the `ISS-*` link on the 73 Tier 2 checks that lost it"
status: backlog
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
parent: "[[FEAT-0131-The-Suite-Is-Refined]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# Restore the `ISS-*` link on the 73 Tier 2 checks that lost it

TESTING.md already requires it — each Tier 2 test *"references the \`ISS-*\` that created it"*. Measured 2026-08-18: **85 of 158 do**, so 73 have lost the one field that says why they exist.

This is what makes Tier 2 groupable by issue rather than by 46 one-off scenario names, and it is the prerequisite for [[TASK-0526]] — a check cannot rest with its issue if it does not name one.

**Per check, from the note's own text.** A Tier 2 check whose issue cannot be identified is a finding, not a blank to fill: it may be the evidence that the check should be retired ([[TASK-0518]]).

## The premise is refuted, 2026-08-20 — they never had it

This task says the 73 *"have lost"* the field. **They did not lose it. It was never written.**

The pre-migration `docs/tests/ACCEPTANCE_TESTS.md` survives in `your-trainer`'s history (deleted at the migration; last living revision recovered with `git show`). Its Tier 2 section splits exactly:

| Tier 2 headings | count | rows under them |
|---|---|---|
| naming an `ISS-*` — e.g. `## 2.1 Family License on Cold Start (ISS-0108)` | 31 | **85** |
| naming none | 21 | **73** |
| | 52 | **158** |

Those three numbers are the ones this task already carries — *"85 of 158 do, so 73 have lost"* — and they line up with the note corpus at `HEAD` exactly: 158 `tier: 2` checks, 85 with an `ISS-*` in `covers:`, 73 without. **73 is also basis-independent**: the working tree has 164 / 91 / 73.

So the migration was **lossless**. It carried the heading's issue into `covers:` wherever the heading had one, and wrote nothing where it did not, which is the correct behaviour. An attempted excavation by the [[TASK-0517]] method recovered **0 of 73**, and that zero is the evidence rather than a failure of the method: the document cannot supply what it never held.

## What this task actually is

Not a restoration — **original research**. For each of 73 checks, decide from its own text which issue it guards, or that it guards none. The task's own last line already anticipated this: *"A Tier 2 check whose issue cannot be identified is a finding, not a blank to fill: it may be the evidence that the check should be retired ([[TASK-0518]])."* That is now the whole of it, not the tail.

**Left open deliberately.** Filling 73 `covers:` entries by inference would put a guessed link on a check that gates a release, and the guess would be indistinguishable from a recovered one the moment it was written. That is the shape this phase exists to remove.

## Consequence for [[TASK-0526]]

A Tier 2 check can only rest with its issue if it names one, so *rest-with-issue* reaches **85 of 158 today** and cannot reach the other 73 until this is done. Not a blocker for building it — the mechanism is [[ADR-0028]]'s in-flight rule and needs no new code — but its coverage must be stated rather than assumed, or the surface will look like it quieted everything it could.
