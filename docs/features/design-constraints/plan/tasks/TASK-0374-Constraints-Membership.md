---
type: "[[task]]"
id: TASK-0374
aliases: ["TASK-0374"]
title: "The constraints view takes decisions, risks, references, workflows and the brief, beside the designs"
status: backlog
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-10
updated: 2026-08-10
source: ["[[FEAT-0087-Design-Widens-Into-The-Projects-Constraints]]"]
parent: "[[FEAT-0087-Design-Widens-Into-The-Projects-Constraints]]"
effort: M
due: ""
depends: []
blocks: ["[[TASK-0375-Decide-And-Accept-On-The-Constraints-View]]"]
related: ["[[FEAT-0050-Library-Reduction]]", "[[FEAT-0084-One-View-Vocabulary]]"]
tests: []
---

# Constraints membership

## Definition of Done
- [ ] The view holds design (10), adr/decision (10), risk (6), reference (18), workflow (3), architecture/glossary/dashboard (3), and the project brief
- [ ] Requirements are **not** here; they stay nested under their features
- [ ] **The Library view is unchanged and still works** — Edwin's call, 2026-08-10
- [ ] The view has an agreed name covering its contents — "Design" no longer does, and "Project" is taken by mode 1's label for `library`
- [ ] No note type loses its only surface ([[REQ-0025]])

## Steps
- [ ] Widen `_design_groups` to the constraint types, grouped by kind
- [ ] Leave `_library_groups` alone
- [ ] Check [[REQ-0025]]'s guard passes for every type
- [ ] Settle the name with Edwin before the button ships

## Notes
**Library stays** (Edwin, 2026-08-10: *"I do want to keep the library view for now"*). An earlier draft of this task dissolved it; that is reversed.

The overlap is deliberate and bounded: Library is a **file browser** answering *where is that file*, this view is **typed notes** answering *what constrains this project*. A `reference/` note appears in both — one item, two addresses, which is not the second-list failure [[ISS-0068]] warns about. The boundary to watch is Library growing typed groups; at that point the two really would duplicate.

[[REQ-0025]] — *no note type loses its only surface* — is already tested and is the guard that matters when a view's membership changes.
