---
type: "[[requirement]]"
id: REQ-0056
aliases: ["REQ-0056"]
title: "One outcome vocabulary, defined in one document, and a check that fails when the document and the corpus disagree"
status: draft
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
priority: medium
scope: "taxonomy"
implements: "[[FEAT-0137-One-Outcome-Vocabulary-Written-Down-Once]]"
acceptance:
  - "[ ] `TAXONOMY.md` documents exactly one set of outcome values, landed upstream first and synced to every repo."
  - "[ ] Legacy values remain readable and are not presented as current."
  - "[ ] A check reads the documented vocabulary and the corpus, and fails when a live value is undocumented."
  - "[ ] The check is proved by introducing an undocumented value and observing the failure."
covers: []
related: ["[[ISS-0218-Taxonomy-Documents-A-Mark-Vocabulary-The-Data-Abandoned]]", "[[ADR-0029-The-Acceptance-Mark-Vocabulary-Is-Minimals]]", "[[ADR-0034-Three-Axes-Not-One-Word]]", "[[ADR-0037-A-Verdict-Is-An-Event]]"]
tags: [requirement]
---

# One vocabulary, and a check that keeps it one

## Statement

There **shall** be one outcome vocabulary for acceptance verdicts, defined in one document, matching the values the corpus actually carries. A live value that the document does not define **shall** fail a check.

## The defect this is written against

[[ISS-0218]]: `TAXONOMY.md` has documented the single-character vocabulary in **all four repos including upstream** for three weeks, while all 671 notes carry words. It failed nothing, because `acceptance.py` accepts both forms — correctly and deliberately, since a suite mid-migration must keep working.

**Tolerance in the reader plus silence in the gate is what produced it.** Criterion 3 removes the silence without removing the tolerance; those are separable and the migrations depend on the tolerance staying.

## Acceptance criteria

- [ ] One documented set, upstream first.
- [ ] Legacy readable, not presented as current.
- [ ] A drift check exists.
- [ ] The drift check is proved to fail.
