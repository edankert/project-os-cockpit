---
type: "[[task]]"
id: TASK-0541
aliases: ["TASK-0541"]
title: "Seed the check-to-covering-test mapping from the 203 prose annotations, before `automation:` is removed"
status: done
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
parent: "[[FEAT-0138-Coverage-Is-Observed-Not-Declared]]"
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
tags: [task]
---

# Seed first, delete second

## Definition of Done

- [ ] `covered_by:` is extracted from every repo — measured, it holds **nothing anywhere**, and that is recorded rather than assumed.
- [ ] `your-trainer`'s **203** parenthesised annotations (181 `(partially automated`, 22 `(automated`) are extracted with the check id and the class name they name.
- [ ] The 54 distinct JVM classes are listed.
- [ ] The seed is committed **before** [[TASK-0530]] removes `automation:`.

## Done 2026-08-19 — and the seed is larger than the ADR said

`docs/features/verdict-ledger/plan/coverage-seed-your-trainer.json`.

| | ADR-0037 / [[ISS-0198]] | measured 2026-08-19 |
| --- | --- | --- |
| checks with a coverage claim | 203 | **278** |
| distinct JVM classes | 54 | **81** |

**The difference is 75 checks carrying `automation: manual` whose body names a covering test class anyway** — `TST-0020` names `UnitConverterTest`, `TST-0110` names `HardcodedComposeTextTest`, and so on. [[ISS-0198]] measured the *parenthesised annotation* and backfilled `automation:` from it; a check that mentions its covering class in ordinary prose never got one, so it reads `manual` and is invisible to the field entirely.

**That is the standing-claim failure from the other direction, and it is the better argument for decision 8 than the one the ADR makes.** The field does not merely rot after it is written — 75 of these were *never written*, because populating a claim depends on somebody noticing there was a claim to make. Observed coverage does not: the class either emits on a run or it does not.

`covered_by:` was confirmed empty in every repo before extracting, so nothing was lost by it holding nothing.

**Scope note.** This is the *seed extraction* — data preservation guarding [[TASK-0530]]'s removal, and the one cross-stage constraint the plan names. The `@Covers` inversion ([[TASK-0542]]) and the emitter ([[TASK-0543]]) are **not** started: Edwin's goal is Stage 1 only.

## Notes

[[ADR-0037]] decision 8 says seed before deleting; this is that step, and it is the whole reason Stage 2 is not simply "write an emitter".

These annotations are the only record of which machine covers which check. They survived the document migration as prose, were backfilled into `automation:` by [[ISS-0198]], and `covered_by:` was left deliberately empty because they name classes, not `TST-*` ids. Under observed coverage that is no longer a problem — but only if the mapping still exists.
