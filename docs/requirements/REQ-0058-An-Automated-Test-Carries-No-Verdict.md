---
type: "[[requirement]]"
id: REQ-0058
aliases: ["REQ-0058"]
title: "An automated test carries no verdict"
status: implemented
phase: "[[PHASE-039-A-Test-Says-Who-Executes-It]]"
owner: user:edwin
created: 2026-08-19
updated: "2026-08-20"
source: ["[[ADR-0038-The-Suite-Is-The-Verdict]]"]
priority: high
scope: "Every TST-* note whose `command:` is non-empty — 139 fleet-wide on 2026-08-19."
acceptance: ["A note with a non-empty `command:` holding `ready`, `passing` or `failing` is a validator error", "A note with a non-empty `command:` holding `last_run:` or `exit_code:` is a validator error", "`run-tests.py --write` mutates no note frontmatter", "Manual tests keep their verdict, asserted by count before and after"]
implements: "[[FEAT-0139-The-Suite-Is-The-Verdict]]"
verifies: []
related: ["[[ADR-0038-The-Suite-Is-The-Verdict]]", "[[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]]"]
tests: []
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: changes-requested
---

# An automated test carries no verdict

## Statement

A test note that declares a `command:` **must not** hold `ready`, `passing` or `failing`, and **must not** carry `last_run:` or `exit_code:`. Its status vocabulary is lifecycle only — `draft`, `active`, `retired`.

## Acceptance Criteria

- [x] The forbidden-status check ranges over `command:` non-empty, not over `level: acceptance` — `ACCEPTANCE-STATUS`'s domain went 89 → 139 notes; `tests/test_automated_test_holds_no_verdict.py`
- [x] `last_run:` and `exit_code:` are refused on the same population — `TEST-AUTOMATED-EVIDENCE`
- [x] `run-tests.py --write` leaves every note byte-identical — `tests/test_runner_writes_nothing.py`, asserted on bytes rather than on `status`, and the mutant fails 4 of 6
- [x] Manual tests are untouched — `test_a_manual_test_may_still_record_its_verdict` and `test_a_manual_note_can_still_be_stamped`. **Measured correction**: the population is 65 fleet-wide but 5 in this repo, and the migration changed 38 notes here, 0 of them manual

## Notes

This is not a new constraint. `ACCEPTANCE-STATUS` enforces it today as an error over the 89 automated notes at `level: acceptance` — 64% of the domain — and cannot say why it stops there.

## Independent review 2026-08-20 — `changes-requested`

Reviewed by `model:claude-opus-5` from the notes and the diff alone, in a session that never saw the authoring reasoning.

The runner guard holds under mutation: a status write sneaked back through `open().write()`, evading the `"write_text" not in SCRIPT` string assertion, still fails three tests on byte-identity. The `stamp_test_run` refusal is correct, including the `and not aborted` carve-out — the aborted path writes no `status` and no `last_run`, so it does not stamp a verdict. **No finding against this requirement.** It is marked `changes-requested` only because it shares a change with findings 1-5 below; see the review section of [[CHG-20260820-The-Suite-Is-The-Verdict]].

## Second independent review 2026-08-20 — `changes-requested` (verdict stands)

Second pass, `model:claude-opus-5`, fresh context, different session from both the author and the first reviewer.

The runner and refusal guards hold again: disabling `TEST-AUTOMATED-EVIDENCE` in both validator copies fails `test_evidence_of_a_run_is_refused[last_run]` and `[exit_code]`. **The finding is against criterion 1's landing claim, not the rule.** Measured against `your-trainer` at its committed `HEAD`, this requirement's two codes are not at zero: `TEST-AUTOMATED-EVIDENCE` reports **4 errors** (`TST-0016`, `TST-0017` — `last_run:` and `exit_code:` each) and the widened `ACCEPTANCE-STATUS` reports **2**, where the pre-change validator (`5adcbc8`) reports **0** on the same corpus — so the widening introduced them. In `your-trainer`'s working tree `TEST-AUTOMATED-EVIDENCE` is **71**. *"Zero violations at landing"* is true of `project-os-cockpit` and `your-sudoku` only, because the migration was deliberately not run downstream. Not red today only because `your-trainer`'s validator copy predates both rules. Detail in [[CHG-20260820-The-Suite-Is-The-Verdict]] section A.

## Third independent review 2026-08-20 — `changes-requested` (verdict stands)

Third pass, `model:claude-opus-5`, fresh context, a different session from the author and from both prior reviewers.

**The two codes are dated and the guards are not vacuous** — disabling the `TEST-AUTOMATED-STATUS` branch in both validator copies fails three tests, and `PROMOTIONS` carries `2026-11-18` for both, asserted.

**The remaining finding is against the split's shape, not its existence.** It is cut on `level:` rather than on `command:` (`validate_docs_bundled.py:2424`), so the *"a machine-executed test holds no verdict"* rule this requirement states reaches the dated code only for notes that are **not** `level: acceptance`. A note that is both takes `ACCEPTANCE-STATUS`'s undated day-one error — verified by construction: `level: acceptance` + `command:` + `status: passing` is silent under `5adcbc8` and an error under this tree. This module's own docstring puts that population at *"89 of the fleet's 139 automated notes: 64% of the domain"*, and every fleet repo but this one still ships the `run-tests.py` that writes those statuses. Zero in every tree today, so nothing is red — one validator sync plus one run from being so, with no cutover to absorb it.

Measured fleet-wide at `HEAD` this session, this requirement's two codes carry **12** (`TEST-AUTOMATED-STATUS`) and **24** (`TEST-AUTOMATED-EVIDENCE`) across `your-trainer`, `project-os-dev` and `your-health` — six times the 2 and 4 the new `PROMOTIONS` comment records, under a sentence claiming measurement *"against every repo"*. Three docstrings in `tests/test_automated_test_holds_no_verdict.py` (`:15`, `:89`, `:129`) still assert day-one erroring over zero violations. Detail in [[CHG-20260820-The-Suite-Is-The-Verdict]] sections A1 and A2.

## Fourth independent review 2026-08-20 — `changes-requested` (verdict stands)

Fourth pass, `model:claude-opus-5`, fresh context, a different session from the author and from all three prior reviewers.

**The runner and evidence guards hold for a fourth time**, and the split is no longer cut on `level:` — the third pass's finding against its shape is genuinely addressed, and reverting the recut fails two parametrisations of the new matrix.

**The finding is that the recut is incomplete, and criterion 1 states the closed reading.** A command-bearing note that is **not** `level: acceptance`, at `status: ready`, is now reported by nothing: `newly_forbidden` requires `status in TEST_RUNNER_STATUSES` (`passing`/`failing`), and the `elif level == "acceptance"` beneath it does not catch the rest. Executed across all 24 cells of (`level` × `command` × `status`): that one cell is silent under the current tree, **warned** under the immediately preceding commit (`72e2038`), and silent before ADR-0038 — so the widening has been reverted for `ready` over the non-acceptance half of the domain. This requirement's Statement — *"a test note that declares a `command:` **must not** hold `ready`, `passing` or `failing`"* — is enforced for two of its three statuses across the full domain, and for the third only where `level: acceptance` already forbade it.

Criterion 1 reads *"the forbidden-status check ranges over `command:` non-empty, not over `level: acceptance` — domain went 89 → 139"* and is ticked `[x]`. Nothing asserts the gap in either direction: extending the predicate to close it passes the file unchanged. Zero instances at every fleet `HEAD` (50 command-bearing notes, none at `ready`), so latent rather than live — the same standing on which the third pass's A1 was filed blocking, in the more dangerous direction. Detail in [[CHG-20260820-The-Suite-Is-The-Verdict]] section H1.
