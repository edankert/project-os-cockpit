---
type: "[[task]]"
id: TASK-0557
aliases: ["TASK-0557"]
title: "One preparing release per platform — `preparing()` returns one per platform, not one overall"
status: backlog
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
parent: "[[FEAT-0129-A-Release-Names-Its-Own-Contents]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# The decision, made operational

Edwin, 2026-08-19: *"Let's consider one release at the time only, multiple releases should use git branches anyway. We can potentially have multiple releases going on at the same time for different platforms."*

**Two concurrent releases on one platform are a branch, not a schema problem.** That decision is what keeps [[ADR-0037]]'s ledger intact: one working ledger per platform, and sealing assigns it to a release. If two releases were preparing on one platform, a verdict recorded today would belong to neither by construction.

## Definition of Done

- [ ] `publication.preparing()` returns **one release per platform** — a mapping, not a single value.
- [ ] **Two preparing releases on one platform is an error**, not a warning. It is the state the ledger cannot represent, so it must not be reachable quietly.
- [ ] A release with no `platform:` takes them all — the same opt-in rule [[DES-0012]] D4 gives release contents, and the same one [[ADR-0037]] gives the gate.
- [ ] Every consumer of `preparing()` is read for whether it means *the* release or *a* release. The obligation registry especially: a badge counting two releases as one is [[ISS-0068]]'s defect with a new subject.

## Notes

Roughly six call sites. The single-value form should stay as a thin wrapper so they move one at a time — a rename that touches every consumer in one commit is how the last three regressions in this phase were introduced.
