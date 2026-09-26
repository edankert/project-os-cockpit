---
type: "[[task]]"
id: TASK-0235
aliases: ["TASK-0235"]
title: "Resolve a feature's plan by path, not by frontmatter type"
status: done
phase: "[[PHASE-010-Surface-Ownership]]"
owner: user:edwin
created: 2026-07-29
updated: 2026-07-29
source: []
parent: "[[FEAT-0046-Plans-On-The-Feature]]"
effort: S
depends: []
blocks: ["[[TASK-0236-Plan-Nested-Under-Feature]]"]
related: ["[[ISS-0062-Most-Plans-Are-Invisible]]"]
tests: ["[[TST-0022-Surface-Ownership]]"]
---

# TASK-0235 — Plan lookup by path

## Definition of Done
- [ ] `_feature_plan(index, record)` resolves `plan/PLAN.md` relative to a feature note's own directory
- [ ] Returns the `NoteRecord` when the file is indexed, `None` when absent
- [ ] Works for plans with **no frontmatter** — the 19 that `notes_by_type("plan")` cannot see
- [ ] Test asserts the resolved count equals the number of `plan/PLAN.md` files **on disk**, not a literal

## Steps
- [ ] Add the helper to `cockpit.py` near `_features_groups`
- [ ] Derive the plan path from `record.path.parent / "plan" / "PLAN.md"`
- [ ] Look it up through `index.get()` (which holds untyped notes, deriving a title from the H1)
- [ ] Test in `tests/test_surface_ownership.py`: iterate every feature record, count resolved plans, compare against a `docs/features/*/plan/PLAN.md` glob

## Notes

The count assertion is the point, not decoration. A regression to `notes_by_type("plan")` would still return a plausible-looking subset; only a count catches it.

**Assert against the glob, not a literal.** The corpus was 33 plans / 14 typed when [[ISS-0062]] was filed; adding this phase's own five features made it 38 / 19. A frozen number would fail on the next feature anyone creates, and the property being tested is "every plan on disk resolves", not "there are N plans".

See [[ISS-0062]] for why retyping the untyped files is deliberately not the fix.
