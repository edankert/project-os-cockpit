---
type: "[[requirement]]"
id: REQ-0025
aliases: ["REQ-0025"]
title: "No note type loses its only surface"
status: implemented
phase: "[[PHASE-010-Surface-Ownership]]"
owner: user:edwin
created: 2026-07-29
updated: 2026-07-29
source: []
priority: high
scope: "Library reduction and the four type moves in PHASE-010"
acceptance:
  - "Plans reachable from their feature, every PLAN.md on disk"
  - "Risks reachable from the Issues mode"
  - "Changes reachable from the overview, archive included"
  - "Tests reachable from the review desk, all of them"
  - "Decisions reachable from the overview record column"
  - "Designs reachable from the Design mode"
  - "Workflows reachable from the Docs tree"
  - "Library mode still opens and is not empty"
implements: "[[FEAT-0050-Library-Reduction]]"
verifies: []
related: ["[[PHASE-010-Surface-Ownership]]", "[[FEAT-0046-Plans-On-The-Feature]]", "[[FEAT-0047-Risks-On-The-Issues-Surface]]", "[[FEAT-0048-Changes-On-The-Overview]]", "[[FEAT-0049-Review-Desk-As-Record]]"]
tests: ["[[TST-0022-Surface-Ownership]]"]
---

# REQ-0025 — No note type loses its only surface

## Statement

Removing a type's group from Library **must not** be merged before that type is reachable from its new surface. Every note type present in the corpus shall be reachable by navigation — not by search, not by typing a path — from at least one page after the reduction lands.

## Why this is a requirement and not a note in the plan

This phase's only real hazard is ordering. Each Library group is currently the *sole* navigable route to its type for at least three of the seven types being moved, and a reduction commit that lands before its destination silently strands notes. The cockpit has already shipped this exact defect twice in one phase: the design bench was built, tested and unreachable ([[FEAT-0043]]'s premise), and the Library Design group pointed at the note rather than the bench, leaving the render surface with no door into it.

Nothing detects that class of failure. The validator checks the corpus, not the UI's reachability of it; the tests check payload shape, not that a payload is rendered anywhere. So it is written as a gate: [[FEAT-0050]] cannot reach `done` with an unresolved criterion here.

## Acceptance Criteria

Tick only with an evidence pointer, at feature close-out.

- [x] Plans reachable from their feature — **every `PLAN.md` on disk, not only those carrying frontmatter** (33/14 when [[ISS-0062]] was filed; 38/19 after this phase added five features, which is why the assertion is against a glob and not a literal) — evidence: `test_every_plan_on_disk_resolves_to_its_feature` (set equality against a `features/*/plan/PLAN.md` glob, plus a strict-subset assertion on the typed set so the test cannot pass if every plan happens to be typed); manual run step 1 — 38 rows rendered, untyped `agent-verbs`/`agent-hooks`/`task-dispatch` among them
- [x] Risks reachable from the Issues mode, and the Risks stat tile navigates there — evidence: `test_every_risk_appears_in_the_issues_mode`, `test_risks_get_their_own_groups_not_the_issue_buckets`, `test_the_dead_stat_tiles_gained_a_destination[Risks-issues]`; manual run steps 2–3 — 4 risk rows in three severity groups, tile navigates to `issues`
- [x] Changes reachable from the overview, with the pre-existing week/month archive still openable — evidence: `test_the_changes_split_is_a_partition` (recent + buckets == corpus, so nothing falls out of both); manual run step 4 — 5 recent rows, 3 collapsed buckets, May 2026 nesting its week sub-buckets
- [x] Tests reachable from the review desk — the full register, not the `ready`-and-manual queue slice — evidence: `test_the_tests_register_holds_the_whole_corpus` (register set equality with `notes_by_type("test")`, plus `len(runs) < len(register)` so the two cannot be collapsed); manual run step 5 — `Tests · 22/22`, 22 rows
- [x] Decisions reachable from the overview record column, including those past the top-4 cut — evidence: `renderer.ts:10269-10273` — `buildRecordDisclosure` receives `sorted.slice(4)` and renders every remaining ADR inline rather than linking out, so the column is the register and the removed Library group was a duplicate
- [x] Designs reachable from the Design mode — evidence: `test_designs_reach_the_bench_from_the_design_mode` — the reachability guard that lived on the removed Library group moved to `_design_groups` rather than being deleted with it, and additionally asserts the duplicate route is gone
- [x] Workflows reachable from the Docs tree — evidence: `test_workflows_browse_in_the_docs_tree`, `test_workflows_join_the_docs_tree`; manual run step 6 — `workflows/` present in the tree
- [x] Library mode still opens and renders Pinned + Docs tree rather than an empty pane — evidence: `test_library_is_pins_and_the_tree`, `test_library_auto_discovery_still_works_for_vault_types` (vault types still discovered), `test_the_skip_set_is_not_derived_from_the_empty_tuple` (the back-door regression); manual run step 6 — Docs tree renders with `reference/`, `references/`, `workflows/`

## Traceability

- Implements: [[FEAT-0050-Library-Reduction]]
- Verified by: [[TST-0022-Surface-Ownership]], `tests/test_cockpit.py`
