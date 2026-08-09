---
type: "[[task]]"
id: TASK-0357
aliases: ["TASK-0357"]
title: "Obligation groups carry their verb, and Proposals splits into Approve and Accept"
status: backlog
phase: "[[PHASE-023-Levers-For-The-Human]]"
owner: user:edwin
created: 2026-08-09
updated: 2026-08-09
source: ["[[DES-0010-The-Desk-Shows-What-It-Owes]]"]
parent: "[[FEAT-0082-The-Desk-Shows-What-It-Owes]]"
effort: S
due: ""
depends: ["[[ISS-0121-Reviewed-Register-Counts-Settled-Work-As-Owed]]"]
blocks: ["[[TASK-0358-The-Board-Is-The-Desks-Landing]]"]
related: ["[[DES-0005-The-Actuator-Grammar]]"]
tests: []
---

# Obligation groups and verbs in the payload

## Definition of Done
- [ ] `review_queue_payload` emits a `verb` on every group, and the renderer takes its column label from it
- [ ] `Proposals` splits: requirement `draft` → **Approve**, design `proposed` + open ledger offers → **Accept**
- [ ] Removing a group from the payload removes its column with no renderer change (asserted)
- [ ] No obligation vocabulary is declared in TypeScript

## Steps
- [ ] Split the proposals bucket in `review_queue_payload` by note type, preserving the `offered` dedup that keeps a ledger row winning over a status-intake row
- [ ] Add `verb` beside `key`/`label` on each group
- [ ] Extend `tests/test_review_desk.py`: a group with no items still declares its verb; deleting a group drops its column

## Notes
The split is a payload change, not a renderer change — a `draft` requirement is *approved* and an offered design revision is *accepted*, and [[DES-0005]]'s table already distinguishes them. Keeping the vocabulary server-side is the [[ISS-0023]] rule applied before it can be broken rather than after.

Depends on [[ISS-0121]] only in ordering: the re-review column is wrong until the register filter lands, and shipping the board first would make it more prominent.
