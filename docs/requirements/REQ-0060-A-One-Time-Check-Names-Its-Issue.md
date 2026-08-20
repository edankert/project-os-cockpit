---
type: "[[requirement]]"
id: REQ-0060
aliases: ["REQ-0060"]
title: "A check that is not a standing behaviour claim names the issue it verifies"
status: implemented
phase: "[[PHASE-039-A-Test-Says-Who-Executes-It]]"
owner: user:edwin
created: 2026-08-19
updated: "2026-08-20"
source: ["[[ADR-0039-Three-Sections-Derived-Not-Filed]]"]
priority: medium
scope: "Acceptance checks authored after the promotion date; 117 pre-existing instances at HEAD, all in your-trainer, carried by a dated promotion."
acceptance: ["The check warns before the promotion date and errors after", "Pre-existing instances are carried by a dated promotion, never by a blanket exemption", "A newly authored check violating this is refused from day one"]
implements: "[[FEAT-0140-Sections-Are-Derived-Not-Filed]]"
verifies: []
related: ["[[ADR-0039-Three-Sections-Derived-Not-Filed]]", "[[project-os-dev#ADR-0011]]"]
tests: []
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: approved
---

# A one-time check names its issue

## Statement

An acceptance check that is not a standing claim about behaviour **must** name the `ISS-*` it verifies in `covers:`. Without it the check cannot be distinguished from a behaviour claim, and is treated as one.

## Acceptance Criteria

- [x] `CHECK-SUBJECT` warns with a cutover of 2026-11-18, and the test asserts the **date exists** — a justification with no cutover is the permanent-warning tier ADR-0011 forbids
- [~] **Reconciled, and the number was wrong.** Measured at HEAD 2026-08-20: the checkable population is **117**, all in `your-trainer` (an earlier 44 was its working tree) — **85** naming nothing and **32** naming only a `PHASE-*`/`TASK-*`. The 68 figure counted checks with no `ISS-*` *anywhere*, most of which do name a `FEAT-*` and classify correctly. They are carried by the dated promotion rather than by ID: `GRANDFATHERED.yaml` is per-repo, and listing another repo's notes here would exempt nothing where it matters
- [x] A new check naming no subject is reported immediately — `test_a_check_naming_no_subject_is_reported`

## Notes

Measured 2026-08-19: 68 of `your-trainer`'s 164 Tier 2 checks name no `ISS-*` anywhere in the note — not in `covers:`, not in the body. Five more name one outside `covers:` and are a scripted repair. Deriving without this rule would silently classify all 68 as behaviour claims and put them back on the list at every overlapping change, which is the behaviour [[ADR-0039]] exists to remove.

## Independent review 2026-08-20 — `changes-requested`

Reviewed by `model:claude-opus-5` from the notes and the diff alone, in a session that never saw the authoring reasoning.

Not separately refuted. `CHECK-SUBJECT` lands warning-first with a dated cutover, which is what [[project-os-dev#ADR-0011]] clause 3 requires, and the criterion whose count was wrong is marked reconciled rather than ticked — that correction is the right shape. Marked `changes-requested` with its siblings; see [[CHG-20260820-The-Suite-Is-The-Verdict]].

## Second independent review 2026-08-20 — `changes-requested` (verdict stands)

Second pass, `model:claude-opus-5`, fresh context, different session from both the author and the first reviewer.

The mechanism holds: warning-first with a dated cutover is what [[project-os-dev#ADR-0011]] clause 3 requires, and `PROMOTIONS["CHECK-SUBJECT"] == "2026-11-18"` is asserted. **The corrected count is still the wrong tree.** `CHECK-SUBJECT` measured against `your-trainer` at its committed `HEAD` reports **117**, not 44; 44 is its working tree, the same 588 uncommitted files that produced the gate number this change was correcting. The 44 also appears in [[CHG-20260820-The-Suite-Is-The-Verdict]] and in the docstring of `tests/test_automated_test_holds_no_verdict.py:212`.

The gap is not noise: the 74 Tier 3 checks carry `covers: []` and all fire this gate, and they are the population [[ADR-0039]]'s own table calls *67 automated* — reclassified to `Feature tests` with no grandfather and no promotion date, unlike the 68 Tier 2 checks the ADR carried by ID. Detail in [[CHG-20260820-The-Suite-Is-The-Verdict]] sections A and E.

## Third independent review 2026-08-20 — `changes-requested` (verdict stands)

Third pass, `model:claude-opus-5`, fresh context, a different session from the author and from both prior reviewers.

**The mechanism holds and the reader now agrees with it.** `CHECK-SUBJECT` warns with a dated cutover, asserted; and `Suite.missing_issue_refs`, which was a tautology for one commit, now reports the same population — measured this session, **117 = 117** at `your-trainer`'s `HEAD` and **44 = 44** in its working tree, **0** here.

**Criterion 2 was not corrected.** It still reads *"the checkable population is **44**, all in `your-trainer` — 12 naming nothing and 32 naming only a `PHASE-*`/`TASK-*`"*, with no basis and no `HEAD` figure, seventeen lines above this note's own second-pass paragraph saying *"reports **117**, not 44"*. The same 44 also survives in `src/project_os_cockpit/validate_docs_bundled.py:866`, its byte-identical twin `tools/scripts/validate-docs.py:866` — the comment that justifies dating the rule — and `tests/test_automated_test_holds_no_verdict.py:230`. Those are the three places the second pass enumerated, and none of them changed.

The gap is the 74 Tier 3 checks: they carry `covers: []`, all fire this gate, and at `HEAD` none of them carries a `command:`. Detail in [[CHG-20260820-The-Suite-Is-The-Verdict]] section A2.

## Fourth independent review 2026-08-20 — `changes-requested` (verdict stands)

Fourth pass, `model:claude-opus-5`, fresh context, a different session from the author and from all three prior reviewers.

**The `117` is correct and independently reproduced**: measured against `your-trainer` at its committed `HEAD` through this repo's validator, `CHECK-SUBJECT` reports **117**, and **44** in its working tree, with zero in every other fleet repo. Scope, criterion, both validator copies and the test docstring all carry it, and the surviving `44`s are quotations inside review sections, which is the right place for them. `PROMOTIONS["CHECK-SUBJECT"] == "2026-11-18"` is still asserted.

**The finding is the clause after the number.** Criterion 2 reads *"the checkable population is **117** … — 12 naming nothing and 32 naming only a `PHASE-*`/`TASK-*`"*, and 12 + 32 = **44**: the decomposition belongs to the working-tree figure the same sentence withdraws. Measured at `HEAD`: **85** name nothing and **32** name only provenance. Both validator copies and the test docstring avoided this by dropping the breakdown rather than restating it, so it survives here alone. Detail in [[CHG-20260820-The-Suite-Is-The-Verdict]] section H3.

## Fifth independent review 2026-08-20 — `approved`

Fifth pass, `model:claude-opus-5`, fresh context, a different session from the author and from all four prior reviewers. Every cell, mutant and count executed here; fleet counts taken from `git archive HEAD`, never a working tree. Baseline **1878 passed, 3 skipped**, validator OK.

**The corrected decomposition is exact.** Measured against `your-trainer` at `HEAD` with the validator's own `extract_ids`: `CHECK-SUBJECT` reports **117**, of which **85** name nothing (83 carrying `covers: []`, 2 carrying no `covers:` at all) and **32** name only provenance (17 `PHASE-*`, 15 `TASK-*`). 85 + 32 = 117, and 117 is 0 in every other fleet repo. `PROMOTIONS["CHECK-SUBJECT"]` is 2026-11-18 and asserted. No finding.
