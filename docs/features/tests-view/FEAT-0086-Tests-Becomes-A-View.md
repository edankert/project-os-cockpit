---
type: "[[feature]]"
id: FEAT-0086
aliases: ["FEAT-0086"]
title: "Tests becomes a view — the register, the runner, the tier suite and a release gate that can finally fire"
status: done
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-10
updated: 2026-08-10
source: ["[[ADR-0020-Obligations-Live-With-Their-Subject]]", "Edwin 2026-08-10: 'I would like those to become a fully fledged part of the project-os family and would like to make sure we can define / refine and execute acceptance tests there'"]
goal: "Give tests the view they have never had — every test in the corpus, the manual runner moved off the desk, the Tier 1/2/3 suite the contract has always described but no repo has ever instantiated, and the release gate that suite makes possible."
requirements: []
tasks:
  - "[[TASK-0371-The-Tests-View-And-Its-Register]]"
  - "[[TASK-0372-The-Runner-Moves]]"
  - "[[TASK-0373-The-Tier-Suite-And-The-Release-Gate]]"
release: ""
related: ["[[ADR-0020-Obligations-Live-With-Their-Subject]]", "[[FEAT-0018-Verification-Health-Surface]]", "[[FEAT-0049-Review-Desk-As-Record]]", "[[FEAT-0063-The-Acceptance-Runner]]", "[[FEAT-0064-The-Acceptance-Gate]]", "[[FEAT-0072-The-Release-Surface]]", "[[PHASE-024-Acceptance-Witnessed]]"]

---

# Tests becomes a view

## Goal

Tests have no view. The 23 `TST-*` notes are scattered across 16 feature directories and `docs/tests/`, and are surfaced only as a register on the desk, a verification panel on feature and phase pages, and a stat tile. There is nowhere to *look at the tests*.

And the acceptance contract is entirely unbuilt. `tools/instructions/TESTING.md` and the `acceptance-tests` template define Tier 1 (feature, permanent), Tier 2 (regression, references its `ISS-*`), Tier 3 (verification, temporary), the re-run rule, and a release gate: *"a release is blocked while any Tier 1/2 test is unchecked."* Measured 2026-08-10: **no acceptance-test suite instance exists in this repo.** 85 features, 23 test notes, zero tier classification — a gate that has never been able to fire.

This is the one feature in [[PHASE-030]] that is new capability rather than re-homing.

## Scope

**In:**

- A Tests view: every test in the corpus, grouped so a reader can see what is verified and what is not
- The manual runner (`manual_test_steps`, the stepper, `stamp_test_run` and its `## Runs` log) moved from the desk unchanged
- `test @ ready` and manual as the view's obligation, from [[FEAT-0089]]'s registry
- The tier suite: an acceptance-tests instance for this repo, tests classified Tier 1/2/3, rendered
- The release gate's surface — unchecked Tier 1/2 tests listed on a release note in the template's own words

**Out:**

- **The acceptance *runner*** — [[FEAT-0063]]/[[FEAT-0064]] under [[PHASE-024]] own the criterion-by-criterion walk and the `acceptance:` gate. This feature gives them their home instead of the desk; it does not build them.
- Changing what a test *is*, or the `TST-*` storage split (feature-scoped under `plan/tests/`, system-wide under `docs/tests/`). [[LIFECYCLE.md]]'s hybrid rule stands.
- Automating manual tests. A manual pass is evidence that decays ([[STATUSES.md]]); this shows it, it does not replace it.

## Coordination with what already exists

[[FEAT-0018]] owns validator and waiver health at *project* scope. The per-scope verification panel (feature/phase/release) stays where it is — it answers "is this scope verified", which is a different question from "what do we verify". Both read note data only, never a queue. This view is the third member of that family, not a replacement for either.

## Acceptance

- [x] A Tests view exists, listing every `TST-*` in the corpus with status, kind and last run — 23 of 23, set-equality asserted ([[TASK-0371]])
- [x] Manual tests at `ready` appear as this view's obligation and carry its badge — from [[FEAT-0089]]'s registry, and the group and the badge are asserted to be the same number by two different code paths
- [x] The runner works from here, writing the same fields and the same `## Runs` log as before; no write path changed — round trip re-run over real HTTP ([[TASK-0372]]); one disclosure recorded there
- [x] An acceptance-tests instance exists for this repo with at least Tier 1 populated, and tests carry their tier — 27 Tier 1, 7 Tier 2, 2 Tier 3 ([[TASK-0373]])
- [x] An unchecked Tier 1/2 test is visible on a release note as a blocking condition, in the template's wording — the rule is sent by the server, never paraphrased
- [x] **The gate can fire** — it *is* firing, on [[REL-0001]], on the live suite: 34 unchecked Tier 1/2 items
- [x] Staleness uses the project's existing threshold and config source, not a second one ([[ISS-0024]]/[[ISS-0069]]) — there were already two, and the renderer's is gone

## Links

- Decision: [[ADR-0020-Obligations-Live-With-Their-Subject]]
- Contract: `tools/instructions/TESTING.md`, `docs/__templates__/acceptance-tests.md`
- Paths: `src/project_os_cockpit/cockpit.py` (`_tests_register`, `scope_tests_payload`, `manual_test_steps`), `src/project_os_cockpit/note_writes.py` (`stamp_test_run`), `desktop/src/renderer/renderer.ts` (`buildTestRunner`)

## Closed 2026-08-10

Three tasks, and each found something the notes did not predict.

1. **The staleness rule was already duplicated.** The DoD said "not a second one"; there were two — the validator's 90 days on `last_verified` against the renderer's 60 on `last_run`, gated to manual tests. On this corpus one calls 2 tests stale and the other calls 0. The renderer's constant is gone rather than reconciled.
2. **The issue draft did not exist.** `draft_issue_body` had shaped a failing step into an issue since July and had no caller outside its own unit test, while [[TST-0021]] and the run summary both told the reader it was offered. Wired to the endpoint's response — never to a write.
3. **The suite could not have been built from the test notes.** 22 of 23 are pytest modules, all `passing`; a suite built from them would have been fully checked on its first day and the gate would have reported clear having verified nothing. Tier lives on the checkbox, which is what the contract said and what the step did not.

The measurement worth keeping: **92 `TST-*` notes across the twelve repos the cockpit renders, zero tier classification, and a release gate that had never been able to fire.** It fires now, and it is red — 34 unchecked Tier 1/2 items on [[REL-0001]] — which is a more useful state than the green nobody had earned.
