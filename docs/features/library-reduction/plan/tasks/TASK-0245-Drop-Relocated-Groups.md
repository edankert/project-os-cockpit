---
type: "[[task]]"
id: TASK-0245
aliases: ["TASK-0245"]
title: "Drop the Plans, Risks, Tests and Changes groups once their destinations exist"
status: done
phase: "[[PHASE-010-Surface-Ownership]]"
owner: user:edwin
created: 2026-07-29
updated: 2026-07-29
source: []
parent: "[[FEAT-0050-Library-Reduction]]"
effort: S
depends: ["[[TASK-0236-Plan-Nested-Under-Feature]]", "[[TASK-0237-Risks-Group-In-Issues-Mode]]", "[[TASK-0240-Changes-Tile]]", "[[TASK-0241-Tests-Register]]"]
blocks: []
related: ["[[REQ-0025-No-Type-Loses-Its-Surface]]"]
tests: ["[[TST-0022-Surface-Ownership]]"]
---

# TASK-0245 — Drop the relocated groups

## Definition of Done
- [ ] `LIBRARY_RARE_TYPES` is empty and the by-type loop that consumes it is removed
- [ ] `_library_groups` returns only Pinned and the Docs tree for this corpus
- [ ] `_BY_TYPE_SKIP_IN_LIBRARY` names every moved type explicitly, no longer deriving them from `LIBRARY_RARE_TYPES`
- [ ] `_changes_subgroups` survives — it belongs to [[TASK-0239]]'s payload now
- [ ] Every [[REQ-0025]] criterion ticked with evidence

## Steps
- [ ] Confirm all four destinations are `done` before starting — this task is gated, not merely ordered
- [ ] Empty `LIBRARY_RARE_TYPES` and delete the loop in `_library_groups`
- [ ] Rewrite `_BY_TYPE_SKIP_IN_LIBRARY` as an explicit frozenset covering `change`, `adr`, `release`, `risk`, `test`, `workflow`, `plan` plus the canonical types
- [ ] Keep `_changes_subgroups` and its callers in the changes payload
- [ ] Test: library payload group keys are a subset of `{pinned, docs-tree}`; a personal-vault type still gets its auto-discovered group

## Notes

This is the task [[REQ-0025]] was written for. Each of the four groups is currently the sole navigable route to its type, and merging this before its destination strands the notes — a failure nothing in the toolchain detects, because the validator checks the corpus and the tests check payload shape, not reachability.

`release` stays in the skip-set even though the corpus has zero REL notes. A release surface is not part of this phase, and letting `release` fall through to auto-discovery would give a future release corpus a Library group by accident.
