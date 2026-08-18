---
type: "[[task]]"
id: TASK-0488
aliases: ["TASK-0488"]
title: "Drop `tests:` from the feature, the three link fields from the test, and the path fallback"
status: done
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
source: ["[[FEAT-0121-The-Verification-Link-Normalises]]"]
parent: "[[FEAT-0121-The-Verification-Link-Normalises]]"
effort: M
depends: ["[[TASK-0487-Invert-VERIFY]]"]
blocks: []
related: []
tests: []
---

# Drop the second and third encodings

`tests:` leaves `feature.md` and the validator stops reading it. `features:`/`verifies:`/`validates:` leave `test.md`, their content having moved to `covers:`. `_test_feature_ids` loses the path fallback — a test's subjects come from `covers:` alone, and where it lives on disk becomes a filing decision with no semantic weight.

**LIFECYCLE.md's hybrid storage rule stays**, reworded: it describes where to *put* a test, not what a test *verifies*. The acceptance README already draws this distinction for checks — *"that split is a filing decision and it is not the reader's problem"* — and this makes it true of tests too.

**A feature's note stops listing its tests, and the surface renders it instead** — derived from the reverse index, and therefore always right, where the field could only ever be as right as the last person to edit both sides. Nothing is lost from the reader's view; one hand-maintained copy is.

Done when: no note type carries a second encoding, the reverse-rendered list appears where the field used to, and `covers:` is the only answer to *what does this test verify* anywhere in the system.

## Done

- **`tests:` removed from 30 features** and from the 10 snapshot entries that mirrored it.
- **`features:`/`verifies:`/`validates:`/`requirements:` removed from all 43 tests**, their content having moved to `covers:`.
- **The path fallback is deleted** from `_test_feature_ids`. Measured before deleting: exactly **3** tests fleet-wide resolved by path alone, all in this repo, and all three now declare their subject. The other 34 under a feature directory already declared theirs.
- **The cockpit reads `covers:` first and the legacy names after**, because it renders twelve repos and only this one has consolidated. Same rename transition as the validator's, and the same rule: every name it reads points test → subject.

`LIFECYCLE.md`'s hybrid storage rule stays, and means only what it says — where to *put* a test. A guard was added rather than assumed: `test_a_tests_subjects_never_come_from_its_directory` strips a note that still has the `features/<slug>/plan/tests/` shape and asserts the resolver answers with nothing. A resolver that fell back to the directory would answer with the owning feature and pass every other test in the file.
