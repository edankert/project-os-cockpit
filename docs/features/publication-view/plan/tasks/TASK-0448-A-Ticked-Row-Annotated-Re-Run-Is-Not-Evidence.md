---
type: "[[task]]"
id: TASK-0448
aliases: ["TASK-0448"]
title: "A ticked row annotated RE-RUN is not evidence — 53 of them are counted as passed today"
status: backlog
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["[[FEAT-0108-The-Gate-Is-A-Delta-Not-A-Census]]", "Measured against ../your-trainer on 2026-08-16"]
parent: "[[FEAT-0108-The-Gate-Is-A-Delta-Not-A-Census]]"
effort: S
depends: []
blocks: []
related: ["[[ADR-0028-Work-Has-Three-Phases]]"]
tests: []
---

# A ticked row annotated RE-RUN is not evidence

## Why

`TESTING.md` rule 2 says a code change unchecks the tests it overlaps. The practice in `../your-trainer` is softer: the row keeps its tick and gains an annotation.

```
- [x] Trainer reconnects after a dropped ERG session  *(RE-RUN — TASK-0588: control-point write path changed)*
```

**54 rows carry one. 53 are still ticked.** The gate counts every one of them as passed, so the honest blocking number is not 60, it is 113.

This is also why [[TASK-0446]]'s regressed count reads 0 and must not be presented as reassurance. The suite's last commit is the v2.0.5 close-out; v2.1.0 and v2.1.6 both shipped without it being touched at all. **Zero regressed currently means nobody unchecked anything**, and these 53 annotations are the last time anyone did that bookkeeping.

## What

Parse the `RE-RUN (TASK-####: reason)` annotation. A ticked row carrying one is reported in its own group — **stale evidence** — with its task and reason. It is not counted as blocking and it is not counted as satisfied; it is a third thing, and saying so is the whole point.

## Deliberately not decided here

Whether stale rows should **block**. Making 53 rows blocking overnight takes the gate from 60 to 113 and would be a change to what shipping means, decided by a rendering task. It is put on the page, with its number, and the decision is Edwin's.

`TESTING.md` rule 5 — *after a verified release, Tier 3 tests are removed and `RE-RUN` annotations are cleared* — **has never been executed in twelve releases**. 68 Tier 3 rows and 54 annotations survive. That is a suite-lifecycle question and is recorded in the phase note, not solved here.

## Done when

- [ ] the annotation is parsed, including its task id and reason
- [ ] ticked + annotated is its own group with its own count, neither blocking nor satisfied
- [ ] an **unticked** row carrying an annotation is blocking, exactly as today, and is not double-counted
- [ ] the annotation is matched on shape, not on the word `RE-RUN` alone — a row whose prose contains "re-run" is not swept in
- [ ] measured against `../your-trainer`: 54 annotated, 53 ticked, and both figures asserted
