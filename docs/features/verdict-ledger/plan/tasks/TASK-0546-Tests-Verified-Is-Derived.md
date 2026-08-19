---
type: "[[task]]"
id: TASK-0546
aliases: ["TASK-0546"]
title: "`tests_verified:` on a release becomes derived from its sealed ledger"
status: done
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

## Decided 2026-08-19 (Edwin)

*"`tests_verified` should be derived."*

The editorial reading — *an authored list of the tests that mattered* — is declined. Two encodings of one fact is what [[ADR-0032]] spent a decision removing, and the argument does not weaken because the second encoding is short: it drifts, and the drift is silent.

## Definition of Done

- [x] Decided: derived.
- [ ] `tests_verified:` leaves the release template and `SCHEMAS.md`, upstream first ([[ADR-0030]] decision 6).
- [x] `publication.py:167`, `cockpit.py:4574` and the shipped-release page (`publication.py:477`) read the sealed ledger instead.
- [x] The rendered list says which platform's ledger it came from — a release page that lists verified checks without naming the platform is the defect [[ADR-0037]] exists to remove, one level up.
- [x] **[[REL-0001]] is not rewritten.** It predates the ledger and there is nothing for it to derive from; its 13 entries stay as the record of what that release was measured against, and the page falls back to the field when no ledger exists.

## Notes

`tests_verified:` was the honest answer when a release had 13 tests. Under the ledger a release has hundreds of entries and the field becomes a hand-maintained excerpt of a computable set — the [[DES-0012]] failure mode (*"a maintained matrix rots"*) in a smaller frame.

The fallback for pre-ledger releases is the same two-shapes-split-by-time pattern `suite_at` already uses ([[TASK-0545]]) and for the same reason: a shipped release is immutable, so what it holds is a permanent fact about the past.

## Done 2026-08-19 — derived, with the field as fallback

`publication._verified_for` returns every check with a **clearing** entry in that release's sealed ledger, and falls back to the authored `tests_verified:` when there is no ledger for that release.

**`na` and `excused` are in the list and that is not a lie.** They are recorded decisions about this release, and a list of *what we verified* that hid them would be the hand-maintained excerpt this replaces. `fail` and `blocked` are not: neither is a verification.

**`tests_verified_platform` travels beside it.** A release page listing verified checks without naming the platform is this decision's own defect one level up, so the platform is carried rather than remembered by whoever renders it.

**[[REL-0001]] is untouched** and keeps its 13 authored entries — it predates the ledger and has nothing to derive from. The same two-shapes-split-by-time pattern `suite_at` uses, and for the same reason: a shipped release is immutable, so what it holds is a permanent fact about the past.

**The field stays in the schema**, deliberately: it is now the fallback rather than the source, and removing it would delete the only record every pre-ledger release has.
