---
type: "[[task]]"
id: TASK-0214
aliases: ["TASK-0214"]
title: "Design-note convention and validator support"
status: doing
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-27
updated: 2026-07-27
source: ["[[REF-0001-Overview-Redesign-Dossier]]"]
parent: "[[FEAT-0042-Design-Bench]]"
effort: "S"
depends: []
blocks: ["[[TASK-0215]]", "[[TASK-0216]]"]
related: []
tests: []
---

# Design-note convention and validator support

## Definition of Done

- [ ] A design note is `type: "[[reference]]"` with `scope: design-input` and an `asset:` naming a file beside it — the shape [[REF-0001]] already uses, written down rather than inferred
- [ ] The sidecar exposes design notes as a typed collection (id, title, asset path, `design:` back-links, revision count) rather than the renderer re-deriving them from a path regex
- [ ] A validator check reports a design note whose `asset:` does not resolve, and an artifact under `references/design/` that no note claims
- [ ] `design:` back-links resolve both ways: from a FEAT/PHASE to its design, and from a design to everything it specifies
- [ ] No upstream taxonomy change is required

## Steps

- [ ] Document the convention in the reference note template's guidance
- [ ] Add the sidecar collection + endpoint
- [ ] Add the two validator checks, each with an inversion test
- [ ] Verify against the real [[REF-0001]] note, not a fixture

## Notes

Deliberately built on `reference` rather than a new `DES-*` type. A design does have a lifecycle `reference` does not model (`proposed → accepted → implemented | superseded`), and that gap may eventually justify the type — but a note type is an upstream change to TAXONOMY, STATUSES, templates and the validator, and this phase should not open with one.

`_DESIGN_DIR_RE` in `cockpit.py` currently identifies designs by path regex for the Library group. That is the thing to replace: membership by frontmatter, not by where the file happens to sit.
