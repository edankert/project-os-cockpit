---
type: "[[task]]"
id: TASK-0542
aliases: ["TASK-0542"]
title: "The test declares the check it covers — comment-and-grep for v1, one convention per language"
status: backlog
owner: user:edwin
created: 2026-08-19
updated: "2026-08-20"
parent: "[[FEAT-0138-Coverage-Is-Observed-Not-Declared]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# The inversion

## Definition of Done

- [ ] A convention exists for declaring the covered check from inside a test, findable by one grep.
- [ ] It works in this repo (pytest) and in `your-trainer` (JVM) without a shared library — a v1 that needs one ships nowhere.
- [ ] A declaration naming a check that does not exist is an error.
- [ ] Nothing in any note declares coverage.

## Notes

**Why the inversion is the structural fix, not a preference.** A standing `covered_by:` on the check rots silently: rename, delete or `@Ignore` the test and the note keeps asserting coverage while the check leaves the run list permanently, with no signal. With the declaration in the test, deleting the test deletes the claim.

`@Covers("TST-0028")` is the shape; the annotation is not required for v1 and a comment is enough. Choosing an annotation first would make this task depend on shipping a library into two toolchains.

## Re-homed 2026-08-20 — the parent moved and this did not

[[FEAT-0138]] was re-homed from [[PHASE-999]] into [[PHASE-037]] on 2026-08-20 (Edwin). **Its tasks stayed behind**, so a task pointed at a parking-lot phase while the feature it delivers pointed at an active one.

That is not cosmetic: `PHASE-CHILDREN` gates a phase on **notes naming it in `phase:`**, so for as long as this task named `PHASE-999` it was invisible to the gate on the phase that actually owns its work — and `PHASE-999` is never closed, so it was invisible to every gate. A child in a parking lot cannot hold anything open.

The phase's own widening note records the same class of miss one level up: *"FEAT-0138 also pointed at PHASE-999 without ever being listed in it, which is why nothing flagged it."*

**The consequence is deliberate.** [[PHASE-037]] now cannot close while this task is unresolved. That is the honest reading of Edwin's re-homing: if the feature belongs to this phase, so does the work that delivers it.
