---
type: "[[requirement]]"
id: REQ-0040
aliases: ["REQ-0040"]
title: "One verification link, one direction — `covers:` on the test is the only encoding, and nothing derives the relationship from a path"
status: implemented
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
priority: medium
scope: traceability
implements: "[[FEAT-0121-The-Verification-Link-Normalises]]"
acceptance:
  - "[~] Reconciled, narrower than written: `tests:` is gone from `feature.md` and the four legacy fields are gone from `test.md`, but `task`, `issue` and `requirement` still carry `tests:` — 330 live edges fleet-wide against the feature's 62. Widening to those three is decided in principle and was not costed in ADR-0032, so it is filed rather than done silently, and VERIFY skips acceptance-level tests meanwhile so the merged type cannot trip the gate from them."
  - "[x] VERIFY resolves a feature's tests from a reverse index over `covers:`, and reports the same violations it reported before the inversion on the corpus as it stands."
  - "[x] `_test_feature_ids` no longer falls back to the directory path; a test's subjects come from `covers:` alone."
  - "[~] Three of the ten — the path-only ones, all in this repo — carry an explicit `covers:`; the other seven are in `your-health` and `project-os-dev`, which have not synced the template and whose validators do not read the field yet. The 25 genuinely system-wide tests are left empty deliberately. Original: The 10 tests resolvable only by path or by a feature's edge carry an explicit `covers:` — and the 25 genuinely system-wide tests are left empty deliberately, with that stated rather than backfilled."
  - "[x] Zero unreciprocated edges remain in this repo — the eight were read and resolved individually, seven in the feature's favour. Zero unreciprocated edges remain, because there is no second side to reciprocate."
covers: []
related: ["[[ADR-0032-The-Verification-Link-Has-One-Direction]]", "[[ISS-0199-Twenty-Of-Sixty-One-Feature-To-Test-Edges-Are-Not-Reciprocated]]"]
---

# One verification link

Three encodings of one relationship, two of them hand-maintained in opposite directions, already 33% disagreeing. The fix is not a reconciliation rule; it is deleting two of the three.

**The 25 stay empty on purpose.** A backfill that guesses an owner for a system-wide test would replace an honest absence with a plausible wrong answer, which is worse than the gap and much harder to find later.

## Acceptance criteria

- [~] **No note type carries both encodings.** Reconciled, narrower than written: `tests:` is gone from `feature.md` and the four legacy fields are gone from `test.md`, but `task`, `issue` and `requirement` still carry `tests:` — **330 live edges fleet-wide against the feature's 62**. ADR-0032 scoped the decision to features and did not cost the other three, so widening is filed rather than done silently. VERIFY skips acceptance-level tests meanwhile, so the merged type cannot trip the gate from them.
- [x] **VERIFY resolves a feature's tests from a reverse index over `covers:`.** Proved across all twelve repos: 56 findings before, 57 after, and the one difference is a *true* violation the old lookup was blind to (`your-trainer` FEAT-0086 is `done` with TST-0013 never walked).
- [x] **`_test_feature_ids` no longer falls back to the directory path.** Deleted, after measuring that exactly 3 tests fleet-wide depended on it and backfilling all three. Guarded by `test_a_tests_subjects_never_come_from_its_directory`, which strips a note that still has the path shape and asserts the resolver answers with nothing.
- [~] **The ten backfilled.** Three of the ten — the path-only ones, all in this repo — carry an explicit `covers:`. The other seven are in `your-health` and `project-os-dev`, whose validators do not read the field yet; the forward-field fallback covers them so nothing is lost. The 25 genuinely system-wide tests are left empty deliberately.
- [x] **Zero unreciprocated edges remain in this repo.** The eight were read and resolved individually — seven in the feature's favour, one in the test's — and with one encoding there is no second copy to disagree.

## Advanced 2026-08-18

Two criteria are **reconciled rather than ticked**, and both departures are the same shape: the decision was scoped to features and the corpus turned out to hold the same pattern on three more types and in six more repos. Neither was widened silently — the first is filed, the second is bounded by which repos have synced the template.
