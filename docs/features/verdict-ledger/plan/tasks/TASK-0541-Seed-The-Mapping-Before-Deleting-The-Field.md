---
type: "[[task]]"
id: TASK-0541
aliases: ["TASK-0541"]
title: "Seed the check-to-covering-test mapping from the 203 prose annotations, before `automation:` is removed"
status: backlog
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

## Notes

[[ADR-0037]] decision 8 says seed before deleting; this is that step, and it is the whole reason Stage 2 is not simply "write an emitter".

These annotations are the only record of which machine covers which check. They survived the document migration as prose, were backfilled into `automation:` by [[ISS-0198]], and `covered_by:` was left deliberately empty because they name classes, not `TST-*` ids. Under observed coverage that is no longer a problem — but only if the mapping still exists.
