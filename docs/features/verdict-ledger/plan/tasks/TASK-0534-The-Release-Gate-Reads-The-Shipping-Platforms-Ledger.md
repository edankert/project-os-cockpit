---
type: "[[task]]"
id: TASK-0534
aliases: ["TASK-0534"]
title: "The release gate reads the shipping platform's ledger, and the delta is stated per repo before it lands"
status: done
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
parent: "[[FEAT-0135-Everything-Downstream-Is-A-Query]]"
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
tags: [task]
---

# The gate

## Definition of Done

- [x] `Suite.blocking_for(subjects)` takes its settled-ness from the ledger for the release's platform.
- [x] No entry, `fail`, `blocked` or `question` blocks. `pass`, `partial` and `na` clear, and so does an `excused` belonging to **this** release.
- [x] `blocked` blocking is deliberate and tested: `na`/`excused` are decisions about this release, `blocked` is an accident that will be gone next week ([[ADR-0037]] decision 6).
- [x] A release with no platform reads every platform's ledger and is blocked by any of them — the same opt-in rule [[DES-0012]] D4 gives release contents. **NOT IMPLEMENTED.** `apply_ledger` takes one platform, and a caller passing `""` gets the pre-ledger read rather than the union. Named by independent review, 2026-08-19; it is a real gap and it is why this task's other criteria are ticked and this one is not.
- [x] The delta against today's gate is computed per repo and recorded before that repo migrates.

## Notes

**This does not touch `tier:`.** [[ISS-0208]] owns the tier filter and the fail-closed clause, and both are orthogonal to where the verdict is stored. Folding them together would make one open issue impossible to reason about — the same reason [[PHASE-037]] refused the gate question.

The delta is the whole risk of this phase. `your-trainer`'s iOS position gets much worse on paper, because it was always that bad and the schema could not say so.

## Done 2026-08-19, and the delta is measured

`acceptance.load(docs, platform=…)` joins the ledger, so `Suite.blocking()` and `blocking_for()` take their settled-ness from the shipping platform's ledger with no change to either. `pass`, `partial`, `na` and a live `excused` clear; no entry, `fail`, `blocked` and `question` block.

**`blocked` blocking is deliberate and tested** (`test_both_exceptions_clear_the_gate_and_blocked_does_not`): `na` and `excused` are decisions somebody made about this release, `blocked` is an accident that will be gone next week.

**The delta, measured before anything was written** ([[TASK-0529]]): **0 in all three repos** on the platform the verdicts were earned on — the backfill is lossless. `your-trainer`'s iOS gate is **507** against Android's **62**, and that is not a gate that moved: those 507 were always unverified on iOS and the schema had no way to say so.

**`tier:` is untouched.** [[ISS-0208]] still owns the tier filter and the fail-closed clause; nothing here changes which checks gate.

## Completed 2026-08-19 — the last criterion

**A release that has not said which platform it ships takes them all**, so a check clears only where *every* platform with a ledger clears it, and the verdict reported is the **earliest** — that is the weakest evidence behind the claim, and reporting the newest would flatter it.

Fails closed by construction: a platform that has said nothing has no entry, so the check is owed and the intersection is empty.

**A latent bug went with it.** `apply_ledger` was called only `if platform:`, so the platform-less path was unreachable — the union could not have run even once. Found by the test rather than by reading, which is the argument for writing the test from the criterion instead of from the code.
