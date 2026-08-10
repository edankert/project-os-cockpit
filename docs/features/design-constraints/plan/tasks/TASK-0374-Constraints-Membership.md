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
- [ ] The view is named **Intent** (Edwin, 2026-08-10) in both front doors, and its icon is revisited — the current one is a design pin, which stops fitting a view holding decisions and hazards
- [ ] No note type loses its only surface ([[REQ-0025]])

## Steps
- [ ] Widen `_design_groups` to the constraint types, grouped by kind
- [ ] Leave `_library_groups` alone
- [ ] Check [[REQ-0025]]'s guard passes for every type
- [ ] Apply the name **Intent** once, for both renderers ([[FEAT-0084]] single-sources labels — `library` being 'Project' in one and 'Library' in the other is the drift it exists to remove)

## Notes
**Library stays** (Edwin, 2026-08-10: *"I do want to keep the library view for now"*). An earlier draft of this task dissolved it; that is reversed.

The overlap is deliberate and bounded: Library is a **file browser** answering *where is that file*, this view is **typed notes** answering *what constrains this project*. A `reference/` note appears in both — one item, two addresses, which is not the second-list failure [[ISS-0068]] warns about. The boundary to watch is Library growing typed groups; at that point the two really would duplicate.

[[REQ-0025]] — *no note type loses its only surface* — is already tested and is the guard that matters when a view's membership changes.

**Named `Intent`, 2026-08-10.** It covers all eight kinds without straining: the brief (what this is), ADRs (what was decided), designs (what it should look like), risks (what could go wrong), the glossary (what the words mean). It is also already this project's word for the idea — [[DES-0003]]'s intent page, [[FEAT-0077]]'s intent charter — so the view and the charter reinforce each other rather than compete. Reversible: it is a label, and [[FEAT-0084]] makes it a one-line change once single-sourced.
