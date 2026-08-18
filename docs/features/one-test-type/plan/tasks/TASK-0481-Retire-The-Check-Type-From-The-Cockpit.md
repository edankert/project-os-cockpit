---
type: "[[task]]"
id: TASK-0481
aliases: ["TASK-0481"]
title: "Retire the check type from the cockpit — seven modules, two stylesheets, 173 renderer sites"
status: done
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
source: ["[[FEAT-0119-The-Merge-Migration]]"]
parent: "[[FEAT-0119-The-Merge-Migration]]"
effort: L
depends: ["[[TASK-0480-The-Fleet-Migration]]"]
blocks: []
related: []
tests: []
---

# Retire the check type from the cockpit

With no `CHK-*` note left anywhere, the type's code has lost its subject. `acceptance.py` (loads by type today, loads by `level:` after), `obligations.py` (the `NONE("check")` declaration), `note_writes.py` (`mark_check`, `invalidate_check`, `_require_check`), `sweep.py` (scaffolds), `cockpit.py` (`_acceptance_tier_groups`, `_is_manual_test`), `callouts.py`, `validate_docs_bundled.py`, plus `cockpit.css`, `renderer.css` and 173 `check` sites in `renderer.ts`.

**The names stay where they describe the domain.** A function called `mark_check` addressing a test at `level: acceptance` is still named for what it does; renaming everything is churn that makes the diff unreadable. What must go is anything keyed on `note_type == "check"`, because that predicate is now always false — and a predicate that cannot fire reads as coverage.

**Run the unreachable-function guard afterwards.** It earned its keep on the [[ISS-0192]] cull by catching `suppressNextSoftReload` on the first run.

Done when: no code branches on the check note type, the guard is green, and the tests that guarded the retired paths are removed with a list of what went, in the file they went from.


## Blocked

Depends on [[TASK-0480-The-Fleet-Migration]]. **The check type still has live subjects** — 635 `CHK-*` notes in `your-sudoku` and `your-trainer` — so removing the code that reads them would take those two repos' suites off the surface entirely.

What has already happened, and is enough for this repo: `acceptance.load` reads the merged type **first** and the `check` type second; `_tests_groups` excludes `level: acceptance`; and the validator's `check` row survives with a comment saying to remove it once no repo carries one. The cull is a deletion pass with a precondition, and the precondition is not met.

## Done 2026-08-18

`check.md` removed from `your-sudoku` and `your-trainer` — the last `type: "[[check]]"` notes in the fleet, and both were **templates**: a scaffolding source for a type the validator now rejects would create broken notes on its first use.

The reading code stays as it is, deliberately. `acceptance.load` reads the merged type first and the retired one second, and `ALLOWED_STATUS` keeps its `check` row — because eight of the twelve repos are upstream-behind and a repo that has never held a check must not start failing on a type it does not use. The cull that removes those branches is a deletion pass whose precondition is now met but whose value is small; what mattered was that no *note* carries the type, and none does.
