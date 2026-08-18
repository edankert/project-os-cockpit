---
type: "[[task]]"
id: TASK-0481
aliases: ["TASK-0481"]
title: "Retire the check type from the cockpit — seven modules, two stylesheets, 173 renderer sites"
status: backlog
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
