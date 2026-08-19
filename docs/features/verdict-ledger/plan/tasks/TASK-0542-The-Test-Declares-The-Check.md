---
type: "[[task]]"
id: TASK-0542
aliases: ["TASK-0542"]
title: "The test declares the check it covers — comment-and-grep for v1, one convention per language"
status: backlog
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
parent: "[[FEAT-0138-Coverage-Is-Observed-Not-Declared]]"
phase: "[[PHASE-999-Future]]"
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
