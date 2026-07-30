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
reviewed_by: "model:claude-opus-5"
review_date: "2026-07-30"
review_verdict: "approved"
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
- [x] Decisions reachable from the overview record column, including those past the top-4 cut — **originally ticked false; see the review section below.** The claim was that `buildRecordDisclosure` renders every remaining ADR inline, which is true of the function and irrelevant, because the column's *source* had been emptied by this very phase ([[ISS-0065]]). Re-earned 2026-07-30 after the column moved to `GET /api/cockpit/decisions` — evidence: `test_decisions_have_a_payload_of_their_own` (payload set-equality with `notes_by_type("adr")` ∪ `notes_by_type("decision")`), `test_the_record_column_does_not_harvest_a_nav_mode`, and the live pane rendering `Decisions 8 · all accepted` with 8 rows and a `4 older` disclosure. The original pointer `renderer.ts:10269-10273` was also wrong — `sorted.slice(4)` is at `renderer.ts:10617`
- [x] Designs reachable from the Design mode — evidence: `test_designs_reach_the_bench_from_the_design_mode` — the reachability guard that lived on the removed Library group moved to `_design_groups` rather than being deleted with it, and additionally asserts the duplicate route is gone
- [x] Workflows reachable from the Docs tree — evidence: `test_workflows_browse_in_the_docs_tree`, `test_workflows_join_the_docs_tree`; manual run step 6 — `workflows/` present in the tree
- [x] Library mode still opens and renders Pinned + Docs tree rather than an empty pane — evidence: `test_library_is_pins_and_the_tree`, `test_library_auto_discovery_still_works_for_vault_types` (vault types still discovered), `test_the_skip_set_is_not_derived_from_the_empty_tuple` (the back-door regression); manual run step 6 — Docs tree renders with `reference/`, `references/`, `workflows/`

## Traceability

- Implements: [[FEAT-0050-Library-Reduction]]
- Verified by: [[TST-0022-Surface-Ownership]], `tests/test_cockpit.py`

## Independent review — 2026-07-30, changes-requested

Reviewed from the notes and the diff for `bed48ea` in a fresh session (`model:claude-opus-5`, no access to the authoring session's reasoning). Six of the eight criteria were re-derived and hold under mutation. **Criterion 5 is false**, and it is the criterion this requirement exists to protect.

**Criterion 5 — decisions are not reachable from the overview record column.** `fillRecordColumn` (`renderer.ts:10520`) sources every note it renders from `fetchRecordNotes('library')`, which is `GET /api/cockpit/nav?mode=library`. At `bed48ea~1` that harvest returned 149 typed items including 8 ADRs and 21 tests. At `bed48ea` it returns **0** — the reduced payload emits only `docs-tree`, whose items carry no `id`, and `fetchRecordNotes` drops anything without one. So `adrs` is empty, `if (scopedAdrs.length > 0)` never fires, and the Decisions card is not built at all on the project-scope overview. Confirmed at function level and over HTTP against this repo's corpus.

The deduplication argument was circular. "Library's Decisions group is a duplicate of the record column" was true only because *the record column was that same Library payload, reshaped*. Removing the duplicate removed the source. `buildRecordDisclosure` does receive `sorted.slice(4)` as claimed — the function is fine; nothing reaches it.

Blast radius, measured against this corpus: 8 of 9 ADRs have **no** navigation route post-change (`ADR-0000`..`ADR-0006`, `ADR-0008`; `ADR-0007` appears only transiently in `mode=recent` because it was just edited), and no ADR is in the Cmd+P corpus either — `QUICK_CORPUS_MODES` covers features/tasks/issues/design/library plus the tests register and the changes payload, none of which carry a decision. `decisions` is still in `DOC_TREE_EXCLUDED_ROOTS`, whose comment cites "the overview record column" as the dedicated surface that justifies the exclusion. This is precisely the ordering failure the Statement forbids: the group was removed before its destination existed.

**Second, unclaimed regression from the same root cause.** The overview's `Verification` record card (`passing/total`, non-passing test rows, `fillVerificationHealth`) and the attention inbox's `failing`/`ready` test rows in `appendAsyncWaitingRows` (`renderer.ts:5852`) both read the same emptied payload. The Verification card is gone from the project-scope overview. The attention rows are latent only because all 22 tests are currently `passing`. No note mentions either.

**Criterion 5's evidence pointer does not resolve.** `renderer.ts:10269-10273` lands on scoped-exit evidence-chip code; the cited `sorted.slice(4)` is at `10572-10573`. Criterion 5 is also the only one of the eight with neither a test nor a manual step — a single source-line reference is its whole evidence, and that is the criterion that turned out false.

**What survived refutation.** Criteria 1, 2, 3, 4, 7 and 8 were mutation-tested, not merely re-read. Reverting `_feature_plan` to a `notes_by_type("plan")` lookup fails 2 tests; dropping rows from either register fails; dropping items from the changes split fails (and `total` is sourced independently from `len(records)`, so the partition assertion is not tautological); removing `navMode` from the Risks or Tests tile fails; pointing a tile at the wrong mode fails; re-admitting a type to `LIBRARY_RARE_TYPES` or gutting `_BY_TYPE_SKIP_IN_LIBRARY` fails; re-adding `workflows` to `DOC_TREE_EXCLUDED_ROOTS` fails. Criterion 6 (designs) holds; its guard genuinely moved rather than being deleted with the group.

**To clear this.** Give decisions a real destination and re-tick criterion 5 against a test that asserts reachability of the *rendered* source rather than the shape of the function that would render it — the record column needs a payload that survives the reduction (a decisions endpoint, or a `mode`/register the reduction does not empty). Do the same for the Verification card. Then correct the criterion-5 line pointer. Until then this requirement should not be `implemented` and [[FEAT-0050]] should not be `done`.
## Re-review — 2026-07-30, approved

Second pass, same fresh-context session, against the working tree ([[ISS-0065]]'s fix, uncommitted). **Criterion 5 is now true and the requirement's Statement holds.**

Verified end to end rather than read: `GET /api/cockpit/decisions` returns all 8 ADRs with `rel` and `status` populated, sorted `ADR-0008`..`ADR-0001`, every one `accepted` — which is what makes the live pane's `Decisions 8 · all accepted` with a `4 older` disclosure the expected render. `fillRecordColumn` sources from it and from `registers.tests`; `fetchRecordNotes` is gone from the file.

I also ran the property this requirement actually asserts, rather than its eight proxies: a sweep of every record in the corpus against the union of all nine nav modes plus the decisions, changes and register payloads. **No canonical type has an unreachable note.** Every type's only miss is its `__templates__/` entry, which is excluded by design. The earlier "8 of 9 ADRs" figure in the review section above was my own imprecision — the 9 counted `__templates__/adr.md`; there are 8 real ADRs and all 8 now reach the record column.

Two pre-existing gaps the sweep surfaced, neither caused by this phase nor by the fix, recorded so they are not rediscovered as new: 13 of 21 `reference` notes are outside the Docs tree (4 templates, 9 container-directory `README.md` files under excluded roots), so [[ISS-0065]]'s "references browse in the Docs tree" is true of the 8 real references and not of the boilerplate; and `ARCHITECTURE.md`, `GLOSSARY.md`, `DASHBOARD.md` reach no surface, having never been in a `rare:` or `by-type:` group either.

The re-tick is honest in the way that matters: it records that the criterion was originally ticked false and why, rather than quietly flipping to true. That admission is worth more than the fix.
