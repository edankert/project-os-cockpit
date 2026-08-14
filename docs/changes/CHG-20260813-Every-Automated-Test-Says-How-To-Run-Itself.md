---
type: "[[change]]"
id: CHG-20260813-Every-Automated-Test-Says-How-To-Run-Itself
title: "Every automated test says how to run itself"
status: merged
owner: user:edwin
created: 2026-08-13
updated: 2026-08-13
source: ["Edwin 2026-08-13: 'close the already fixed items and the fix the items suggested in the order suggested' — the fourth and last item"]
commit: ""
pr: ""
impacts: ["what tools/scripts/run-tests.py can execute", "which hand may write a test's status", "what release verification can refresh"]
issues: ["[[ISS-0130-Nine-Automated-Tests-Cannot-Be-Re-Run-By-The-Machine]]", "[[ISS-0163-The-Entrypoint-Rule-Is-One-Repos-Test-Not-The-Templates]]"]
features: []
reviewed_by: model:claude-opus-5
review_date: 2026-08-14
review_verdict: changes-requested
related: ["[[PHASE-011-Unproven-Claims]]", "[[ADR-0010]]", "[[ISS-0066-Test-Coverage-Registers-Drift-By-Hand]]", "[[REL-0001-The-Human-Has-Levers]]"]
---

# Every automated test says how to run itself

## Summary

`tools/scripts/run-tests.py` could execute **one** of this repo's 24 test notes. It can now execute **22**; the other two are procedures a person walks and say so.

*Corrected 2026-08-14 after independent review: that sentence is true of `run-tests.py` and was stated more broadly elsewhere in this note, which was wrong. **`entrypoint:` is a template field** (`docs/__templates__/test.md`, `SCHEMAS.md`) that `tools/skills/release-verification/SKILL.md` step 7 reads, and **six notes already carried a complete runnable command in it** — TST-0010/0012/0013/0014/0015/0016. So seven notes could say how to run themselves, not one; what only one could do was be executed by the runner that writes statuses. Nine notes now carry both fields naming the same module, with nothing asserting they agree.*

The gap was not that the tests were failing. All 22 pass, and passed before. It was that `status: passing` on 21 of them was a sentence somebody typed, with no way for a machine to check it — on notes whose verification dates ranged from 2026-07-05 to 2026-08-10, against a codebase that changed substantially on the last of those. *(Corrected: 13 of the 22 carried 2026-08-10, not the 07-05..08-02 range first written.)*

## Behaviour that changed

- **`run-tests.py` now has 22 entrypoints where it had 1.** Release verification's step 7 can re-run them, so a `STALE` verdict can return to `CURRENT` by machine instead of by hand.
- **Every one of those 22 statuses is now the runner's output.** [[ADR-0010]] took `passing`/`failing` away from authors in June; until today the mechanism reached one note.
- **A test note that declares nothing is no longer silently automated-and-unrunnable.** It fails `tests/test_test_entrypoints.py`.
- **An executable test now reports the date it ran, not a date somebody typed.** The freshness rule's field order became conditional on whether a note carries a `command:` — see below; without it all 22 notes would have displayed a date up to 39 days stale beside a green run from minutes ago.
- Nothing about what may write, what may push, or what is refused.

## How the statuses were written, which is the point

Not by editing frontmatter. `command:` was resolved for each note from what that note already claimed — its `path:` field or its `## Running it` prose — and then `run-tests.py --write` ran all 22 and stamped `status`, `last_run` and `exit_code` from the exit code:

```
passing=22  failing=0  unrunnable=0
```

This ordering is forced rather than chosen: adding `command:` flips a note from manual to executable, and `TEST-FIELDS` then rejects a runner status with no `last_run`. The validator makes the dishonest version of this change fail.

## Documentation Coverage (All Types Considered)

- features: not-applicable
- requirements: not-applicable
- tasks: not-applicable
- issues: updated ([[ISS-0130]] fixed), new ([[ISS-0163]])
- tests: updated (22 notes gained an entrypoint and a machine-written status)
- workflows: not-applicable
- decisions: not-applicable — [[ADR-0010]] already decided this; nothing had applied it
- risks: not-applicable
- changes: new
- snapshot: updated

## Evidence

Four guards, each run against the defect it describes:

| guard | mutation | result |
|---|---|---|
| `test_every_automated_test_declares_an_entrypoint` | TST-0001 loses its `command:` — the pre-fix state | fails |
| `test_every_declared_entrypoint_names_files_that_exist` | an entrypoint names a moved module | fails |
| `test_a_manual_test_is_left_manual` | a note is exempt by omission rather than by saying so | fails |
| `test_the_known_manual_tests_stay_exempt` | TST-0011 is handed an entrypoint it cannot honour | fails |
| `test_an_executable_test_reports_its_run_not_an_older_typed_date` | the unconditional `last_verified`-first order is restored | fails |
| `test_a_manual_test_still_reports_its_typed_date` | same mutation, from the manual side | fails |

## The change exposed a latent defect in the freshness rule

`cockpit._test_last_verified` preferred `last_verified` over `last_run` unconditionally, and was right to when written — 22 of 23 notes were manual-shaped. This change inverted that population in an afternoon, and every newly-executable note kept a `last_verified` from weeks earlier. All 22 would have displayed the typed date; the oldest, 2026-07-05, was 39 days into a 90-day staleness threshold while running green.

Fixed as a rule rather than as data: an executable test reads `last_run` first ([[ADR-0010]] makes the runner the only hand that may write its status), a manual test reads `last_verified` first (nothing runs it). Latent until today because every note carrying both fields had the same date in each. *(Corrected 2026-08-14: 15 of 24 carried both immediately before the change, not one — the property held, the count offered as its reason did not.)*

## Follow-ups

- [ ] [[ISS-0163]] — the same check in the template, where the other eleven repos would get it. This repo does not own `validate-docs.py`.

## Independent review — 2026-08-14, `changes-requested`

Fresh context, separate session, never saw the authoring reasoning; same model family as the author (`model:claude-opus-5`, recorded in `reviewed_by` per [[project-os-dev#ADR-0013]]). **The code is sound and nothing here asks for a revert.** All six Evidence rows reproduce, `run-tests.py` reports `passing=22 failing=0 unrunnable=0` on a fresh dry run, every `command:` resolves to a module the note itself names, and the freshness rule is guarded in both directions — restoring the unconditional `last_verified`-first order fails two tests, and an unconditional `last_run`-first order fails `test_a_manual_test_still_reports_its_typed_date`. What is requested is corrections to the record, which is what this note is.

**Finding 1 — the premise omits `entrypoint:`, and it is the field the release gate actually reads.** *"no way for a machine to check it"* is not what the corpus said. `entrypoint:` is a template field (`docs/__templates__/test.md:13`; `docs/__templates__/SCHEMAS.md:193`, *"Repo-relative command/script to run"*), and immediately before this change **ten notes carried it — six with a complete, runnable command**: TST-0010, TST-0012, TST-0013, TST-0014, TST-0015 and TST-0016 each carried `.venv/bin/python -m pytest tests/test_*.py`. Ran TST-0010's verbatim: `19 passed`. [[ISS-0130]] quotes release-verification step 7 as *"If `kind: automated` and `entrypoint` is set: run the entrypoint command"* — and `tools/skills/release-verification/SKILL.md:85` still says exactly that. So for six of the nine notes the issue is titled after, the gate whose reach is the stated motivation could reach them. The true and much narrower claim is the one about `run-tests.py`, which reads `command:` and nothing else.

**Finding 2 — the three declaration styles converged on four.** Nine notes now carry both `entrypoint:` and `command:` naming the same module (checked: no drift today), with nothing asserting they agree. *"`command:` is now the entrypoint and `path:` is documentation"* leaves the field literally called `entrypoint` unaccounted for. Either teach `run-tests.py` to fall back to `entrypoint:`, or delete `entrypoint:` from these notes, or add the equality check — but two entrypoint fields with no gate between them is the drift this repo files issues about.

**Finding 3 — *"the single note carrying both fields had the same date in each"* is wrong by 14.** Immediately before this change **15 of 24** notes carried both `last_run` and `last_verified`; at `bf0c5f5`, when `_test_last_verified` was written, **4 of 23** did. Every one of them matched, so the conclusion — latent until the sweep — holds, and the original docstring's *"22 of 23 carry `last_verified`; TST-0022 carries only `last_run`"* was accurate when written. It is the count offered as the reason that is false, and it is repeated in `cockpit.py` and in [[ISS-0130]].

**Finding 4 — *"last verified between 2026-07-05 and 2026-08-02"* is the wrong population.** That is the range for the nine notes [[ISS-0130]] originally counted. Of the **22** this change swept, thirteen carried `last_verified: 2026-08-10` — the very date the note calls *"a codebase that changed substantially"* — so the freshest were three days old, not weeks. The 39-day figure for the oldest (TST-0010, 2026-07-05) is correct, and all 22 would indeed have shown a typed date older than their run.

**Finding 5 — "Four guards" heads a table of six rows.** [[ISS-0130]] gets this right by splitting them (four, then *"two more"*); merging the tables here kept the old count.

**Not defects.** `1 of 24` carrying a `command:` is exact (TST-0022; TST-0024's is the empty string). The two exemptions are correctly `kind: manual`. Eighteen of the notes this change stamped `passing` still carry no `reviewed_by`, so the validator's `[REVIEW]` warnings apply to them — pre-existing, not introduced here, and worth naming since this note is about what a machine may assert. `status: draft` is outside `ALLOWED_STATUS["change"]` (`{merged, reverted}`) and no gate catches it: `STATUS-VALUE` reads the snapshot, and `STATUS-TYPE` checks only that a type has a table, never that a value is in it.
