---
type: "[[adr]]"
id: ADR-0032
aliases: ["ADR-0032"]
title: "The verification link has one direction and one encoding — `covers:` on the test, and a feature never lists its tests"
status: proposed
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
decision_date: ""
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
supersedes: ""
superseded: ""
related: ["[[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]]", "[[ISS-0195-Two-Types-Carry-One-Act]]", "[[ISS-0199-Twenty-Of-Sixty-One-Feature-To-Test-Edges-Are-Not-Reciprocated]]", "[[FEAT-0121-The-Verification-Link-Normalises]]"]
tags: [conventions, schema, testing, traceability]
---

# The verification link has one direction

## Status

**Proposed 2026-08-18.** Independent of [[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]] in principle — either could land without the other — and coupled to it in practice, because ADR-0031's one uncovered collision is the gate this decision removes.

## Context

Edwin, 2026-08-18: *"a TST currently is linked from a feature and therefore cannot span multiple features … and a CHK currently links back to the features, that sounds to me like the same functionality but in 2 different directions, I think we should normalise this?"*

The premise about spanning is wrong and the conclusion is right. Measured across the fleet:

**A test is not confined to one feature by frontmatter — 20 of 117 already name more than one.** What confines is the **path**: LIFECYCLE.md's hybrid storage puts feature-scoped tests under `docs/features/<slug>/plan/tests/`, and 37 tests sit there, bound to one feature by their location. `_test_feature_ids` treats the path as a fallback — *"the declared edge wins, the path is the fallback only for a note that declares nothing"* — so it binds only the 3 tests that declare nothing and live there.

**One relationship, three encodings:**

| encoding | direction | population |
|---|---|---|
| directory path | feature → test | 37 tests |
| the test's `features:` / `verifies:` / `validates:` | test → feature | 82 tests |
| the feature's `tests:` | feature → test | **61 edges** |

**And it has already drifted: 20 of the 61 feature→test edges are not reciprocated** — a third. The feature claims a test verifies it and the test does not say so (8 in this repo, 10 in `your-health`, 2 in `project-os-dev`). Both sides are hand-maintained and nothing reconciles them, so the drift is silent and it is already here.

A check has exactly **one** encoding, `covers:`, and fans out further than tests do: **112 of 669 cover more than one subject**, up to seven.

## Decision

**The test's `covers:` is the single encoding of what a test verifies, in the single direction test → subject.**

1. **`covers:` replaces `features:` / `verifies:` / `validates:` on the test type.** One field name, inherited from the check schema, carrying `[[FEAT-…]]`, `[[ISS-…]]` and `[[REQ-…]]` alike. It is the foreign key on the many side, which is the form that scales to 669 rows and the form that cannot drift because there is nothing to drift against.
2. **A feature no longer carries `tests:`.** The field is removed from `feature.md` and the validator stops reading it.
3. **VERIFY inverts.** The gate builds the reverse index once at load — the tests whose `covers:` names this feature — instead of reading the feature's list. The cockpit's index already has a backlink graph; `validate-docs.py` builds its own, because it works from `SNAPSHOT.yaml` plus note frontmatter and has no index.
4. **The path stops being a link.** LIFECYCLE.md's hybrid storage stays as a **filing convention with no semantic weight** — where a test lives is a filing decision, exactly as the acceptance README already says of checks. The path fallback in `_test_feature_ids` is deleted.
5. **The backfill is bounded and measured.** Of the 35 tests that declare no feature: **3** resolve by path only, **7** by the feature's `tests:` edge, and **25** by neither — genuinely system-wide and correctly unowned. So **10 notes** need a `covers:` written, and the 20 unreciprocated edges are resolved in the same pass rather than carried across.

## Consequences

The relationship becomes queryable in one direction and answerable in both, because a reverse index is derivation and a second hand-written field is duplication. [[ISS-0199-Twenty-Of-Sixty-One-Feature-To-Test-Edges-Are-Not-Reciprocated]] is closed by construction: with one encoding there is no second copy to disagree.

**It removes the collision [[ADR-0031]] could not dissolve.** VERIFY reads a feature's `tests:` and demands `passing`; an acceptance test rests at `active`. Deleting the field means an acceptance test can never appear in that lookup, so the merged type cannot trip the gate — by construction rather than by an exemption for `level: acceptance`.

**The cost is a real inversion in template-owned code**, and a feature's note stops listing its own tests, which some readers will miss. The answer is that the surface can render it — derived, and therefore always right — where the field could only ever be as right as the last person to edit both sides.

## Alternatives considered

- **Keep both directions and add a validator rule that they agree.** Rejected: it makes the drift loud instead of removing it, and 20 existing violations would have to be fixed before the rule could be turned on anyway — at which point one side is redundant.
- **Normalise the other way — the feature's `tests:` wins.** Rejected by the fan-out: 669 checks pointing at features is a field on 669 notes; the same relationship expressed on the feature side is a list of hundreds of ids on a handful of notes, and it is the side already measured drifting.
- **Leave the path as a fallback.** Rejected: it is the encoding that produced Edwin's original impression that a test cannot span features, and a link that exists only when another one is absent is a rule nobody can state.
