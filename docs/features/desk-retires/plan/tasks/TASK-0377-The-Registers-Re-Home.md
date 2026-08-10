---
type: "[[task]]"
id: TASK-0377
aliases: ["TASK-0377"]
title: "The reviewed register joins the record surfaces, and stops counting settled work as owed"
status: done
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
- [x] The reviewed register (103 verdicts — **104** by the time it moved) renders among the record surfaces, beside ADRs and the verification card
- [x] It no longer reports settled work as owed — [[ISS-0121]] closes with this: 104 verdicts, **0 owed**
- [x] The owed/settled predicate comes from the registry, not from a second implementation in the renderer — the server's `_verdict_is_owed`, read through the row's `owed` flag
- [x] The tests register is already gone to [[FEAT-0086]]; nothing register-shaped remains on the desk

## Steps
- [x] Move the register; `isOwedVerdict` already reads the server's flag (ISS-0121 did that), so the move carried no predicate with it
- [x] Verify against the corpus: all `changes-requested` rows are terminal and read as settled — 0 of 104 owed
- [x] Keep the inverse case working — preserved by leaving the predicate server-side rather than filtering in the card

## Notes
[[ISS-0121]] is a member of [[PHASE-030]] precisely so this move fixes it rather than relocating it. A register that counts settled work as owed is wrong wherever it renders, and moving it would have preserved the defect at a new address.

The inverse case is the one that will be missed: filtering purely on "subject is terminal" also hides a legitimate re-review of finished work.

## Done 2026-08-10

**Its own endpoint, not a slice of the queue.** `GET /api/cockpit/reviewed` serves it, rather than reaching into `review_queue_payload["registers"]["reviewed"]`. Sourcing a record card from a payload named for a page that is being retired is exactly the harvest [[ISS-0065]] was — a card whose contents depend on a surface about to stop existing.

**The card shows what is owed and counts the rest.** The desk listed both halves because it was a queue; the record column is not, so the card lists the owed rows and says *"104 verdicts recorded, none owed"* underneath. Today that means it renders a single honest line where the desk once showed a section headed **Changes requested · 10** of which zero were real.

**Project scope only.** A per-phase verdict list would need every note's verdict filtered against the scope's items, which the stats payload does not carry — and a card silently showing the project's verdicts on a phase page would be worse than no card.

The inverse case [[ISS-0121]] warned about is preserved by *not acting*: the predicate stays in `cockpit._verdict_is_owed`, with its known limitation written down, rather than becoming a `filter` in the renderer that would have to re-derive it.
