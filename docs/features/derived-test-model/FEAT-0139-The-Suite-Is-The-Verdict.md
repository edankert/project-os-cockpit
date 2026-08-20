---
type: "[[feature]]"
id: FEAT-0139
aliases: ["FEAT-0139"]
title: "The suite is the verdict — an automated test stops carrying one, and the gate asks whether its command resolves"
status: done
phase: "[[PHASE-039-A-Test-Says-Who-Executes-It]]"
owner: user:edwin
created: 2026-08-19
updated: "2026-08-20"
source: ["[[ADR-0038-The-Suite-Is-The-Verdict]]"]
goal: "A test note declaring a `command:` records that a machine executes it and nothing about whether it passed; the VERIFY gate is discharged by the command resolving."
requirements: ["[[REQ-0058-An-Automated-Test-Carries-No-Verdict]]"]
tasks: ["[[TASK-0559-The-Runner-Reports-And-Does-Not-Write]]", "[[TASK-0560-The-Forbidden-Status-Check-Widens]]", "[[TASK-0561-The-Verify-Gate-Asks-Whether-The-Command-Resolves]]", "[[TASK-0562-Strip-The-Verdict-From-Forty-Nine-Notes]]", "[[TASK-0563-The-Test-Run-Actuator-Reports]]", "[[TASK-0564-Correct-The-Two-Documents-That-State-The-Reverse]]"]
release: ""
acceptance: ""
design: ""
related: ["[[ADR-0038-The-Suite-Is-The-Verdict]]", "[[project-os-dev#ADR-0010]]", "[[ISS-0239-The-Runner-Stamps-Failing-On-A-Missing-Device]]", "[[ISS-0209-The-Acceptance-Gate-Reaches-No-Fleet-Repo]]"]
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: approved
tags: [feature, testing]
---

# The suite is the verdict

## Goal

`status: passing` on a note a machine executes is a claim CI already answers, and answers better — it cannot notice a renamed test, and a `command:` that stops resolving can. This feature removes the claim and moves the gate onto the thing that self-corrects.

## Scope

- `run-tests.py` reports and stops writing.
- The forbidden-status rule widens from `level: acceptance` to every note carrying a `command:` — 89 notes to 139.
- The `VERIFY` gate is discharged for an automated test by its command resolving.
- 49 notes are stripped of a verdict they should not hold.

## Out of Scope

- Manual tests. All 65 that genuinely record a human verdict keep `status:` and its staleness clock, untouched.
- The 582 ledger-tracked acceptance checks, whose verdicts [[ADR-0037]] already moved.

## Acceptance

- [ ] `run-tests.py --write` changes no note's `status:`, `last_run:` or `exit_code:`
- [ ] A note with a `command:` holding `passing` is a validator **error**
- [ ] A feature reaching `done` against an automated test is gated on the command resolving, not on a stamped status
- [ ] The 49 stamped notes carry no verdict, per repo, measured before and after

## Independent review 2026-08-20 — `changes-requested`

Reviewed by `model:claude-opus-5` from the notes and the diff alone, in a session that never saw the authoring reasoning.

The runner, the actuator refusal and the widened forbidden-status rule all survive mutation. **What does not is the `Broken command` obligation this feature introduces**: deleting its wiring in `cockpit.py` passes all 1854 tests, and the validator's use of `resolve_command` is unguarded the same way. Finding 1 in [[CHG-20260820-The-Suite-Is-The-Verdict]].

## Second independent review 2026-08-20 — `changes-requested` (verdict stands)

Second pass, `model:claude-opus-5`, fresh context, different session from both the author and the first reviewer. The runner-writes-nothing guard and the cockpit refusal both survive re-mutation; disabling `TEST-AUTOMATED-EVIDENCE` in both validator copies fails two tests. The finding is that *"zero violations at landing"* holds for this repo and `your-sudoku` and not for `your-trainer` — **4 errors at its `HEAD`, 71 in its working tree**, plus 2 new `ACCEPTANCE-STATUS` errors the widening introduced. See [[REQ-0058]] and [[CHG-20260820-The-Suite-Is-The-Verdict]] section A.

## Third independent review 2026-08-20 — `changes-requested` (verdict stands)

Third pass, `model:claude-opus-5`, fresh context, a different session from the author and from both prior reviewers. The runner guard and the actuator refusal hold again under re-mutation, and disabling the new `TEST-AUTOMATED-STATUS` branch in both validator copies fails three tests, so the split is not vacuous.

**The finding is that the split was cut on the wrong field.** `validate_docs_bundled.py:2424` branches on `level == "acceptance"` before it looks at `command:`, so a note that is both reaches `ACCEPTANCE-STATUS` — a **day-one error** — and never the dated code. Constructed and executed: `level: acceptance` + `command:` + `status: passing` is silent under the pre-change validator (`5adcbc8`) and an error under this one. That is the newly-widened behaviour landing without a cutover over what this change's own test module measures as *"89 of the fleet's 139 automated notes: 64% of the domain"*, while every other fleet repo still ships the `run-tests.py` that writes exactly those statuses. Zero everywhere today, so not a breach of ADR-0011 clause 3 — one sync plus one run from being one.

Three docstrings in `tests/test_automated_test_holds_no_verdict.py` (`:15`, `:89`, `:129`) still assert the day-one erroring the fix removed. Detail in [[CHG-20260820-The-Suite-Is-The-Verdict]] sections A1 and A2.

## Fourth independent review 2026-08-20 — `changes-requested` (verdict stands)

Fourth pass, `model:claude-opus-5`, fresh context, a different session from the author and from all three prior reviewers. Every mutant applied and executed here; every count measured at `HEAD`.

**The recut is the right line and its matrix is not vacuous** — reverting the split to its `level`-first form fails two parametrisations — but it is incomplete. A command-bearing note that is not `level: acceptance`, at `status: ready`, is reported by nothing: silent before ADR-0038, **warned** by the immediately preceding commit, silent again now. All 24 cells of (`level` × `command` × `status`) were executed and that is the only one that does not land where the record says; the six-case matrix omits it, and closing it breaks no test. Zero instances at every fleet `HEAD`, so latent rather than live. The runner guard and the actuator refusal hold for a fourth time. Detail in section H1.

Full detail in [[CHG-20260820-The-Suite-Is-The-Verdict]], section *Fourth independent review*.

## Fifth independent review 2026-08-20 — `approved`

Fifth pass, `model:claude-opus-5`, fresh context, a different session from the author and from all four prior reviewers. Every cell, mutant and count executed here; fleet counts taken from `git archive HEAD`, never a working tree. Baseline **1878 passed, 3 skipped**, validator OK.

**The recut is complete and its matrix is right in every cell.** All 16 cells executed against the validator, all 16 agreeing with `_SPLIT_MATRIX` on code and severity, plus four extra level values that land with their case-folded equivalents. Five mutants applied and none survived — restoring the old clause fails exactly the cell it dropped. The runner guard and the `stamp_test_run` refusal hold for a fifth time. No finding against this feature; the one open item this round is [[ISS-0240]]'s prose, in section *Fifth independent review* of [[CHG-20260820-The-Suite-Is-The-Verdict]].
