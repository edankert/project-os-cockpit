---
type: "[[requirement]]"
id: REQ-0046
aliases: ["REQ-0046"]
title: "No unrecognised state may be absorbed into the group that asserts a pass"
status: approved
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
priority: high
scope: "tests view"
implements: "[[FEAT-0127-Every-Row-In-The-Tests-View-Is-A-Test]]"
acceptance:
  - "[ ] `Verified` is entered by a positive test, never as a fallback. A status the chain does not name lands in a visible group that says so."
  - "[ ] No note that is not a test appears in the tests view."
  - "[ ] The five `level: system` acceptance tests in your-trainer are levelled deliberately, each with its reasoning recorded."
  - "[ ] Guarded generally — on the fallback behaviour, not on the three ids the corpus happens to contain today."
covers: []
related: ["[[ISS-0212-Retired-Documents-Render-As-Verified-Tests]]", "[[ISS-0213-Acceptance-Tests-Carrying-Level-System]]"]
tags: [requirement]
---

# Fail loud, not into the pass bucket

The same shape as [[ADR-0034]]'s fail-closed clause and the unrecognised-mark rule: **when a classifier meets something it does not understand, the safe direction is the one that asks for a person.** `Verified` is the least safe possible destination — it is the only group whose label is a claim about evidence.

`retired` is the instance the corpus contains. The requirement is about the fallback, which is why criterion 4 forbids a guard keyed on the three ids.

## Acceptance criteria

- [ ] `Verified` requires a positive test.
- [ ] No non-tests in the view.
- [ ] The five levels set deliberately.
- [ ] Guarded on the general case.
