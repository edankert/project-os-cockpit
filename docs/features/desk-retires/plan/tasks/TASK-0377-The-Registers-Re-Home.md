---
type: "[[task]]"
id: TASK-0377
aliases: ["TASK-0377"]
title: "The reviewed register joins the record surfaces, and stops counting settled work as owed"
status: backlog
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-10
updated: 2026-08-10
source: ["[[FEAT-0090-The-Desk-Retires]]"]
parent: "[[FEAT-0090-The-Desk-Retires]]"
effort: M
due: ""
depends: ["[[TASK-0369-The-Obligation-Registry]]"]
blocks: ["[[TASK-0378-The-Route-Retires]]"]
related: ["[[ISS-0121-Reviewed-Register-Counts-Settled-Work-As-Owed]]", "[[FEAT-0049-Review-Desk-As-Record]]"]
tests: []
---

# The registers re-home

## Definition of Done
- [ ] The reviewed register (103 verdicts) renders among the record surfaces, beside ADRs, changes and designs
- [ ] It no longer reports settled work as owed — [[ISS-0121]] closes with this
- [ ] The owed/settled predicate comes from the registry, not from a second implementation in the renderer
- [ ] The tests register is already gone to [[FEAT-0086]]; nothing register-shaped remains on the desk

## Steps
- [ ] Move the register; drop `isOwedVerdict` in favour of the registry's predicate
- [ ] Verify against the corpus: all 10 `changes-requested` rows are terminal and must read as settled
- [ ] Keep the inverse case working — a verdict written *after* its subject went terminal is a genuine re-review request and must not be filtered away

## Notes
[[ISS-0121]] is a member of [[PHASE-030]] precisely so this move fixes it rather than relocating it. A register that counts settled work as owed is wrong wherever it renders, and moving it would have preserved the defect at a new address.

The inverse case is the one that will be missed: filtering purely on "subject is terminal" also hides a legitimate re-review of finished work.
