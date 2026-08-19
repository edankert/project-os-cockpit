---
type: "[[task]]"
id: TASK-0546
aliases: ["TASK-0546"]
title: "`tests_verified:` on a release becomes derived from its sealed ledger, or is explicitly kept as authored"
status: backlog
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
parent: "[[FEAT-0135-Everything-Downstream-Is-A-Query]]"
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
tags: [task]
---

# The release already lists what it verified, by hand

A `[[release]]` note carries `tests_verified:` — [[REL-0001]] lists 13 — and the shipped-release page renders it (`publication.py:167`, `cockpit.py:4574`, `publication.py:477`).

**A sealed ledger answers the same question and cannot drift.** Leaving both is a second encoding of one fact, which is precisely what [[ADR-0032]] spent a decision removing for the verification link, and what [[ADR-0037]] argues against for `automation:` and for applicability.

## Definition of Done

- [ ] Decided: `tests_verified:` is derived from the sealed ledger, or it is deliberately kept as an authored summary with the reason recorded.
- [ ] If derived: the field is removed from the release template and schema, and the page reads the ledger.
- [ ] If kept: the ADR says what it means that is not in the ledger, because *"it is convenient"* is how two encodings of one fact get justified.
- [ ] [[REL-0001]] is not rewritten either way — it predates the ledger, and there is no ledger for it to derive from.

## Notes

`tests_verified:` was the honest answer when a release had 13 tests. Under the ledger a release has hundreds of entries and the field becomes a hand-maintained excerpt of a computable set — the [[DES-0012]] failure mode ("a maintained matrix rots") in a smaller frame.

The decision is genuinely open: an authored list of *the tests that mattered for this release* is a different thing from *every check with an entry*, and one of them is editorial. That is the case to make or to decline.
