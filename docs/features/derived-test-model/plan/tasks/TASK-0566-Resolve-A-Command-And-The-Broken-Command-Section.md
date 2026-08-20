---
type: "[[task]]"
id: TASK-0566
aliases: ["TASK-0566"]
title: "Resolve a `command:` to its target, and the `Broken command` section"
status: done
phase: "[[PHASE-039-A-Test-Says-Who-Executes-It]]"
owner: user:edwin
created: 2026-08-19
updated: "2026-08-20"
source: []
parent: "[[FEAT-0140-Sections-Are-Derived-Not-Filed]]"
effort: "M"
due: ""
depends: []
blocks: []
related: []
tests: []
---

# Resolve a `command:` to its target, and the `Broken command` section

## Definition of Done
- [ ] A resolver answers whether the target a command names exists
- [ ] `Broken command` renders when non-empty and is absent when empty
- [ ] Proved on constructed input, and the mutant fails

## Steps
- [ ] Extract the target: a path for pytest/python, a class for `--tests` / `class=`
- [ ] Return three answers — resolves, does not resolve, nothing checkable — never two
- [ ] Construct a repo where a covering test is deleted, and assert the check appears

## Notes

**This cannot be proved from the corpus.** Measured 2026-08-19 across all 139 automated notes fleet-wide: 134 resolve, 5 name nothing checkable, **0 fail**. A corpus test would pass whether or not the code works — the trap [[TASK-0556]]'s child sort fell into. Constructed input, and execute the mutant.

*Nothing checkable* is a third answer on purpose: folding it into either of the other two makes 5 notes lie.
