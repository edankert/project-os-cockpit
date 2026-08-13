---
type: "[[change]]"
id: CHG-20260813-Every-Automated-Test-Says-How-To-Run-Itself
title: "Every automated test says how to run itself"
status: draft
owner: user:edwin
created: 2026-08-13
updated: 2026-08-13
source: ["Edwin 2026-08-13: 'close the already fixed items and the fix the items suggested in the order suggested' — the fourth and last item"]
commit: ""
pr: ""
impacts: ["what tools/scripts/run-tests.py can execute", "which hand may write a test's status", "what release verification can refresh"]
issues: ["[[ISS-0130-Nine-Automated-Tests-Cannot-Be-Re-Run-By-The-Machine]]", "[[ISS-0163-The-Entrypoint-Rule-Is-One-Repos-Test-Not-The-Templates]]"]
features: []
related: ["[[PHASE-011-Unproven-Claims]]", "[[ADR-0010]]", "[[ISS-0066-Test-Coverage-Registers-Drift-By-Hand]]", "[[REL-0001-The-Human-Has-Levers]]"]
---

# Every automated test says how to run itself

## Summary

`tools/scripts/run-tests.py` could execute **one** of this repo's 24 test notes. It can now execute **22**; the other two are procedures a person walks and say so.

The gap was not that the tests were failing. All 22 pass, and passed before. It was that `status: passing` on 21 of them was a sentence somebody typed, with no way for a machine to check it — on notes last verified between 2026-07-05 and 2026-08-02, against a codebase that changed substantially on 2026-08-10.

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

Fixed as a rule rather than as data: an executable test reads `last_run` first ([[ADR-0010]] makes the runner the only hand that may write its status), a manual test reads `last_verified` first (nothing runs it). Latent until today because the single note carrying both fields had the same date in each.

## Follow-ups

- [ ] [[ISS-0163]] — the same check in the template, where the other eleven repos would get it. This repo does not own `validate-docs.py`.
