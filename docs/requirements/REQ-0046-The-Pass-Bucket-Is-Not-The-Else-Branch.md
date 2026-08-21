---
type: "[[requirement]]"
id: REQ-0046
aliases: ["REQ-0046"]
title: "No unrecognised state may be absorbed into the group that asserts a pass"
status: implemented
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-21"
priority: high
scope: "tests view"
implements: "[[FEAT-0127-Every-Row-In-The-Tests-View-Is-A-Test]]"
acceptance:
  - "[x] `Verified` is entered by a positive test, never as a fallback — [[TASK-0506]]; a status the chain does not name lands in a visible group that says so."
  - "[x] No note that is not a test appears in the tests view — [[ISS-0212]], the three `status: retired` run plans are no longer typed as tests."
  - "[x] The five `level: system` acceptance tests in your-trainer are levelled deliberately, each with its reasoning recorded — [[ISS-0213]]'s judgement table; TST-0015 and TST-0018 are `acceptance`, and TST-0011/0012/0013 are read individually with the reasoning written down. **Applying the last three is deferred with the issue**, on a cost the issue measures and Edwin has not ruled on."
  - "[x] Guarded generally — on the fallback behaviour, not on the three ids the corpus happens to contain today ([[TASK-0506]])."
covers: []
related: ["[[ISS-0212-Retired-Documents-Render-As-Verified-Tests]]", "[[ISS-0213-Acceptance-Tests-Carrying-Level-System]]"]
tags: [requirement]
---

# Fail loud, not into the pass bucket

The same shape as [[ADR-0034]]'s fail-closed clause and the unrecognised-mark rule: **when a classifier meets something it does not understand, the safe direction is the one that asks for a person.** `Verified` is the least safe possible destination — it is the only group whose label is a claim about evidence.

`retired` is the instance the corpus contains. The requirement is about the fallback, which is why criterion 4 forbids a guard keyed on the three ids.

## Acceptance criteria

- [x] `Verified` requires a positive test.
- [x] No non-tests in the view.
- [x] The five levels set deliberately.
- [x] Guarded on the general case.

## Implemented 2026-08-21

Criterion 3 is the only one that needs a sentence. It asks for the five levels to be **set deliberately, with the reasoning recorded** — and that is what [[ISS-0213]] did: each of the five was read rather than pattern-matched on its name, and the judgement is a table in that note. Two were already resolved; three are argued to be acceptance checks by their own words.

**Applying the last three is a different act and it is not this requirement's.** Relevelling `TST-0011`/`TST-0012` puts three blocking checks into `your-trainer`'s gate, and `TST-0013` carries 107 checkbox rows behind what would become one blocking check — the document-suite shape [[PHASE-035]] migrated away from. That is Edwin's call on another repo's data, it is recorded on the issue, and the issue is parked under [[PHASE-999]] rather than closed over.

The criterion says *"levelled deliberately, each with its reasoning recorded"*. It is.
