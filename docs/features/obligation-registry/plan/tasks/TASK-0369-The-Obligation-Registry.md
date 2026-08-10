---
type: "[[task]]"
id: TASK-0369
aliases: ["TASK-0369"]
title: "One module enumerates every obligation kind with its predicate, owning view and verb"
status: backlog
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-10
updated: 2026-08-10
source: ["[[ADR-0020-Obligations-Live-With-Their-Subject]]"]
parent: "[[FEAT-0089-The-Obligation-Registry-And-The-Badges]]"
effort: M
due: ""
depends: []
blocks: ["[[TASK-0370-Badges-On-The-View-Buttons]]"]
related: ["[[TASK-0357-Obligation-Groups-And-Verbs-In-The-Payload]]", "[[ISS-0121-Reviewed-Register-Counts-Settled-Work-As-Owed]]"]
tests: []
---

# The obligation registry

## Definition of Done
- [ ] One module declares every kind: predicate, owning view, verb
- [ ] Kinds cover `requirement @ draft`, `design @ proposed`/offered, `adr @ proposed`, `issue @ triage`, `test @ ready` + manual, `change` without a review verdict, and `changes-requested` on a live subject
- [ ] `QUEUE_INTAKE_STATES` is replaced by it, not duplicated alongside it
- [ ] A settled subject is never owed — [[ISS-0121]]'s predicate lives here
- [ ] A kind with no owning view fails a test; a view claiming an unknown kind fails a test
- [ ] No obligation vocabulary in TypeScript

## Steps
- [ ] Write the registry beside `statuses.py`, which is the same shape of single-source and the precedent that earned it
- [ ] Serve it, and give each view its own slice
- [ ] Port `review_queue_payload`'s intake states across, deleting the originals
- [ ] Test in the style of `tests/test_status_vocabulary.py`

## Notes
Carries forward the one idea worth keeping from the superseded desk board: [[TASK-0357]] specified *"the verb ships in the payload beside the group; no obligation vocabulary in TypeScript."* Same rule, wider scope.

`change` is the kind [[ADR-0020]] originally missed — 116 notes, **76 without a review verdict**, a `GATE_BEARING_TYPE` whose warnings become errors on 2026-10-23. Its owning view is the Overview, per the ADR's amendment. Whether the historical ones count as owed is left open there; the registry should make that a **parameter** (a cutoff date) rather than a hard-coded answer, so the decision can be taken with the count in view.
