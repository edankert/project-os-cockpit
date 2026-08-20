---
type: "[[task]]"
id: TASK-0569
aliases: ["TASK-0569"]
title: "Invalidation narrows to Feature tests"
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

# Invalidation narrows to Feature tests

## Definition of Done
- [ ] A change invalidates only checks in the Feature tests section
- [ ] A Regression check, once completed, is not re-opened by a later change
- [ ] The `mark: rerun` path still lets a person re-open one explicitly

## Steps
- [ ] Scope the invalidation predicate to the derived Feature tests section
- [ ] Leave the explicit `rerun` mark reachable for every section

## Notes

This is [[ADR-0039]] decision 2, and it is the clause carrying risk: nothing re-opens a settled regression check automatically. The argument is that a bug we did not expect to recur, recurring, was by definition one that should have had a `command:`.

A `pass` already survives the seal ([[ADR-0037]] decision 7), so *never comes back* is the default once invalidation stops reaching it.
