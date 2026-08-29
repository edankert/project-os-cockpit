---
type: "[[test]]"
id: TST-0081
aliases: ["TST-0081"]
title: "The drift check fails when the fleet falls behind — the failing branch is exercised, and a missing validator is not silently a divergence of zero"
status: active
covers: ["[[TASK-0585]]"]
owner: user:edwin
created: 2026-08-29
updated: 2026-08-29
reviewed_by: model:claude-opus-5
review_date: 2026-08-29
review_verdict: changes-requested
review_response: "All nine findings acted on; the verdict stands as written. CODE (1-5): the add-only merge loop, the partly-populated-list path and `main()` itself all now have tests -- `main()` was reached by nothing, so the dry-run snapshot preview AND ISS-0257's artefact pruning were both unguarded. `RULE_RE` gained a `\\b`, because `emit` was matching as a SUBSTRING inside `promotion_emit(` and three of the four call names in the alternation were doing nothing; the fixture now carries a wrapped call and a `report,`-prefixed one, so both sub-patterns are load-bearing. The writer balances brackets (a flow list closing at column 0 left an orphan `]` and produced unparseable frontmatter -- ISS-0260 reintroduced by the tool that found it) and reads CRLF and a BOM; `apply_plan` reports an unreadable note instead of raising, because it writes file by file AFTER the forced validator copy. NUMBERS (6): all four reproduce the reviewer's way -- your-sudoku 57 not 59, your-trainer 625 not 628, the fleet 682/716 not 669, and 784 is a raw diff where the label said whitespace-normalised (776). Corrected in PHASE-041, TASK-0583, TASK-0584, ISS-0209 and the CHG, with the propagation path named. GOAL (7): PHASE-041 now says in its own body that nothing runs the drift check, so the goal sentence is not met even though criterion 4 literally is. LEDGER (8): your-trainer ISS-0378 files the fifteen VERIFY findings, and the ledger entry now records both irregularities -- that the file says it only shrinks, and that `cutover:` frames these as promotion-time debt when they were invisible rather than exempted. WORDING (9): the BACK_FIELDS comment no longer claims to mirror an order it deliberately reverses, and TASK-0580's box no longer describes a removal the tool does not do. Ten mutants re-run, every one now fails a named test; 42 tests, suite green, validator 0 errors."
review_response_date: 2026-08-29
phase: "[[PHASE-041-The-Gate-Runs-Where-The-Checks-Are]]"
source: ["[[ISS-0209-The-Acceptance-Gate-Reaches-No-Fleet-Repo]]"]
scope: system
level: unit
entrypoint: ""
command: ".venv/bin/pytest tests/test_fleet_drift.py -q"
last_verified: ""
issues: ["[[ISS-0209]]"]
tasks: ["[[TASK-0585]]"]
artifacts: []
related: ["[[FEAT-0143]]"]
---

# The drift check fails when the fleet falls behind

Automated, in `tests/test_fleet_drift.py`.

## What it pins

**That it fails.** A guard whose failing branch has never been seen is an assumption. The test constructs a repo whose validator diverges past the threshold and requires a non-zero exit; it also constructs one at exactly the threshold and requires zero, because an off-by-one on a threshold turns a guard into noise or into nothing.

**That absence is not agreement.** A repo with no `tools/scripts/validate-docs.py` must be reported as *absent*, and a missing or unreadable upstream must be reported as *cannot compare* — two outcomes, neither of them "0 lines diverged, all good". This is the failure this whole phase is about: a check that reports success because it could not look.

**That the gate is counted, not inferred.** `_acceptance_is_settled` occurring zero times is the finding [[ISS-0209]] opens with. The check reports the count per repo, and the test pins that a validator without it is reported as gateless even when its line divergence is small.

## Why a threshold rather than exact equality

Because `merge`-owned files and per-repo `STATUSES.md` overrides mean a fleet repo is legitimately allowed to differ, and a check that demands byte equality would be turned off within a week. The threshold's value and its reason are recorded next to it; the test pins the boundary behaviour, not the number.


## Independent review — 2026-08-29, `model:claude-opus-5`, `changes-requested`

Fresh context, separate session; same model family, recorded as provenance (ADR-0013). `RULE_RE` is the drift check's entire sensor, and it is complete against upstream's 52 codes today — but the fixture exercises only the simplest call shape, so two of its three sub-patterns are unguarded:

- Reducing `\s*` to `[ \t]*` — i.e. the regex can no longer span a newline — passes all 12 tests while blinding the check to **10 of upstream's 52 codes**, including `VERIFY-ACCEPTANCE`, the rule this phase exists to deliver.
- Dropping `(?:report,\s*)?` passes all 12 while losing **3** codes, again including `VERIFY-ACCEPTANCE`.
- Dropping `promotion_emit` from the alternation passes all 12; it loses nothing today only because every promoted code is also emitted in a matching shape elsewhere.

A code invisible to the regex is subtracted from *both* sides, so a repo genuinely missing that rule reports `ok`. `UPSTREAM_VALIDATOR` in the fixture should carry a multi-line `promotion_emit(\n    report, "CODE", …)` site.

Two further survivors: swapping the arguments to `line_divergence` (the `lines` column and ISS-0259's published 619 are unchecked), and narrowing `ACCEPTANCE_RE` to drop its whitespace tolerance — a quoted `level: "acceptance"` is not matched by the current regex either, and under-counting checks un-gates a repo silently, which is the failure mode this note names. Nine other mutants were killed, including the threshold boundary, `ABSENT` handling, exit code 2, the gate count, `--gate-all`, and the direction of the `missing` set difference.

Separately: this note and PHASE-041 read as though a build fails when the fleet falls behind. Nothing runs this script — `.git/hooks/pre-commit.local` is not installed here or in any fleet repo, and CI cannot run it by design. That is stated in the hook header; it is not stated next to the claim.
