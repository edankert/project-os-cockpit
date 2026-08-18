---
type: "[[requirement]]"
id: REQ-0040
aliases: ["REQ-0040"]
title: "One verification link, one direction — `covers:` on the test is the only encoding, and nothing derives the relationship from a path"
status: draft
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
priority: medium
scope: traceability
implements: "[[FEAT-0121-The-Verification-Link-Normalises]]"
acceptance:
  - "[ ] No note type carries both a forward and a reverse encoding of the same verification relationship: `tests:` is gone from `feature.md`, and `features:`/`verifies:`/`validates:` are gone from `test.md`."
  - "[ ] VERIFY resolves a feature's tests from a reverse index over `covers:`, and reports the same violations it reported before the inversion on the corpus as it stands."
  - "[ ] `_test_feature_ids` no longer falls back to the directory path; a test's subjects come from `covers:` alone."
  - "[ ] The 10 tests resolvable only by path or by a feature's edge carry an explicit `covers:` — and the 25 genuinely system-wide tests are left empty deliberately, with that stated rather than backfilled."
  - "[ ] Zero unreciprocated edges remain, because there is no second side to reciprocate."
covers: []
related: ["[[ADR-0032-The-Verification-Link-Has-One-Direction]]", "[[ISS-0199-Twenty-Of-Sixty-One-Feature-To-Test-Edges-Are-Not-Reciprocated]]"]
---

# One verification link

Three encodings of one relationship, two of them hand-maintained in opposite directions, already 33% disagreeing. The fix is not a reconciliation rule; it is deleting two of the three.

**The 25 stay empty on purpose.** A backfill that guesses an owner for a system-wide test would replace an honest absence with a plausible wrong answer, which is worse than the gap and much harder to find later.
