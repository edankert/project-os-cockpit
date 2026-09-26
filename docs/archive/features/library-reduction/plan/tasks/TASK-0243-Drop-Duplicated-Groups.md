---
type: "[[task]]"
id: TASK-0243
aliases: ["TASK-0243"]
title: "Drop the Design and Decisions groups — both are duplicates of existing surfaces"
status: done
phase: "[[PHASE-010-Surface-Ownership]]"
owner: user:edwin
created: 2026-07-29
updated: 2026-07-29
source: []
parent: "[[FEAT-0050-Library-Reduction]]"
effort: XS
depends: []
blocks: []
related: ["[[TASK-0212-Design-Input-References]]", "[[FEAT-0043-Design-Top-Level-Surface]]"]
tests: ["[[TST-0022-Surface-Ownership]]"]
---

# TASK-0243 — Drop the duplicated groups

## Definition of Done
- [ ] The `design` group is gone from `_library_groups`
- [ ] `adr` is gone from `LIBRARY_RARE_TYPES`
- [ ] Designs still reachable from the Design mode; ADRs still reachable from the overview record column
- [ ] `_BY_TYPE_SKIP_IN_LIBRARY` still skips both, so auto-discovery does not resurrect them

## Steps
- [ ] Remove the design-group block from `_library_groups` (`cockpit.py:2369-2389`)
- [ ] Remove `"adr"` from `LIBRARY_RARE_TYPES`
- [ ] Keep both names in the skip-set (it is derived from `LIBRARY_RARE_TYPES`, so add them explicitly)
- [ ] Test: neither key appears in the library payload; the design mode and record column are unaffected

## Notes

Independent of the rest of [[PHASE-010]] — neither type loses a route, because neither route was unique. The Design group duplicated the Design mode's own `~design/<id>` URLs; the Decisions group duplicated a record column that renders the full set inline via `buildRecordDisclosure`.

Verify the skip-set explicitly. It is currently `frozenset({...}) | frozenset(LIBRARY_RARE_TYPES) | frozenset(DOC_TREE_INLINE_TYPES)`, so shrinking `LIBRARY_RARE_TYPES` shrinks the skip-set as a side effect — and `adr` at 8 notes clears `_BY_TYPE_MIN_COUNT`, which would bring the group straight back under a different key.
