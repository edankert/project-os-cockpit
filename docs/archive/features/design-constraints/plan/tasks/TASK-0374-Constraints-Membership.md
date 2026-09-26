---
type: "[[task]]"
id: TASK-0374
aliases: ["TASK-0374"]
title: "The constraints view takes decisions, risks, references, workflows and the brief, beside the designs"
status: done
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
- [x] The view holds design (10), adr/decision (10), risk (6), reference (18), workflow (3), architecture/glossary/dashboard (3), and the project brief
- [x] Requirements are **not** here; they stay nested under their features
- [x] **The Library view is unchanged and still works** — Edwin's call, 2026-08-10
- [x] The view is named **Intent** (Edwin, 2026-08-10) in both front doors, and its icon is revisited — the current one is a design pin, which stops fitting a view holding decisions and hazards
- [x] No note type loses its only surface ([[REQ-0025]])

## Steps
- [x] Widen `_design_groups` to the constraint types, grouped by kind
- [x] Leave `_library_groups` alone
- [x] Check [[REQ-0025]]'s guard passes for every type
- [x] Apply the name **Intent** once, for both renderers ([[FEAT-0084]] single-sources labels — `library` being 'Project' in one and 'Library' in the other is the drift it exists to remove)

## Notes
**Library stays** (Edwin, 2026-08-10: *"I do want to keep the library view for now"*). An earlier draft of this task dissolved it; that is reversed.

The overlap is deliberate and bounded: Library is a **file browser** answering *where is that file*, this view is **typed notes** answering *what constrains this project*. A `reference/` note appears in both — one item, two addresses, which is not the second-list failure [[ISS-0068]] warns about. The boundary to watch is Library growing typed groups; at that point the two really would duplicate.

[[REQ-0025]] — *no note type loses its only surface* — is already tested and is the guard that matters when a view's membership changes.

**Named `Intent`, 2026-08-10.** It covers all eight kinds without straining: the brief (what this is), ADRs (what was decided), designs (what it should look like), risks (what could go wrong), the glossary (what the words mean). It is also already this project's word for the idea — [[DES-0003]]'s intent page, [[FEAT-0077]]'s intent charter — so the view and the charter reinforce each other rather than compete. Reversible: it is a label, and [[FEAT-0084]] makes it a one-line change once single-sourced.

## Done 2026-08-10

`Designs 10 · Decisions 11 · Risks 6 · Workflows 3 · Reference 10`.

**Unblocked by Edwin's risk decision** (ISS-0128): a risk is a standing constraint on the project rather than a problem you have, so the six left the Issues navigator in the same change. One type, one owning view — leaving them in both would count them twice in [[FEAT-0089]]'s badges, or neither. Guarded by `test_risk_appears_in_intent_and_not_in_issues`.

**Requirements deliberately did not move**, and that is asserted rather than assumed: 32 notes turn on the line, and a requirement bounds one feature while an ADR or a risk bounds the project.

**Container `README.md` signposts are excluded** from Reference. [[ISS-0125]] measured `reference` doing three unrelated jobs; only the project singletons belong here, and the nine directory markers keep their home in the Library tree, so nothing is orphaned.

### A regression this task caught

[[TASK-0381]]'s status-stripping glued the closing `---` onto the last frontmatter line (`tags: [design]---`), and **all seven standing documents silently stopped parsing** — `type=None`, `id=None`, invisible to every payload that reads by type.

The validator passed. The suite passed. The standing checks passed, because they read the file with a regex rather than as a note. It surfaced only because this view rendered `Reference · 3` where more was expected.

Repaired, and guarded by `test_every_standing_document_still_parses_as_a_note` — which asserts they are **notes**, not that the text looks right. A shape assertion would have passed too.
