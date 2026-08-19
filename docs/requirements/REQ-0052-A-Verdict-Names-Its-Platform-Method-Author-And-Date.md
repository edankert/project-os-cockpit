---
type: "[[requirement]]"
id: REQ-0052
aliases: ["REQ-0052"]
title: "A verdict names its check, its platform, its method, its author and its date, or it is not a verdict"
status: draft
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
priority: high
scope: "acceptance ledger"
implements: "[[FEAT-0133-The-Ledger-Is-The-Only-Place-A-Verdict-Lives]]"
acceptance:
  - "[ ] An entry missing a check, a mark, a date, an author or a method is refused by the validator."
  - "[ ] The platform comes from the ledger the entry is in; no entry may declare a different one."
  - "[ ] `fail`, `partial`, `blocked`, `question` and `na` are refused without a reason; `pass` is not."
  - "[ ] A sealed ledger cannot be modified, proved by a test that attempts it."
  - "[ ] Every event lands in the working ledger for its platform; sealing is what assigns it to a release."
covers: []
related: ["[[ADR-0037-A-Verdict-Is-An-Event]]", "[[ADR-0029-The-Acceptance-Mark-Vocabulary-Is-Minimals]]", "[[ISS-0206-A-Check-Cannot-Belong-To-A-Release]]"]
tags: [requirement]
---

# A verdict carries its three dimensions

## Statement

An acceptance verdict **shall** be recorded as an event naming the check, the outcome, the date, the author and the method, in a ledger whose file identifies the platform and the release. A verdict that cannot name all of these is not recorded.

## Why the reason clause is here and not in convention

[[ADR-0029]] already required a justification for four of six marks. Measured 2026-08-19: **`verdict_reason:` is non-empty on 0 of 671 notes.** The rule held only because nobody ever wrote one of those four marks — it was never enforced against anything that existed. On the event it is enforceable at write time, which is the difference between a rule and a sentence about a rule.

## Acceptance criteria

- [ ] Required fields enforced by the validator, not by convention.
- [ ] Platform comes from the file; an entry cannot contradict it.
- [ ] Reason-bearing marks refused without a reason.
- [ ] Sealed ledgers immutable, proved.
- [ ] Sealing assigns; the working ledger accepts.
