---
type: "[[feature]]"
id: FEAT-0050
aliases: ["FEAT-0050"]
title: "Library reduction — Pinned and the Docs tree, nothing else"
status: done
phase: "[[PHASE-010-Surface-Ownership]]"
owner: user:edwin
created: 2026-07-29
updated: 2026-07-29
source: []
goal: "Library stops being where types go when nobody decided. The seven by-type groups are removed — six because their type now has a purpose surface, one (Workflows) because it joins the Docs tree — leaving Pinned and the files."
requirements: ["[[REQ-0025-No-Type-Loses-Its-Surface]]"]
tasks: ["[[TASK-0243-Drop-Duplicated-Groups]]", "[[TASK-0244-Workflows-Into-The-Docs-Tree]]", "[[TASK-0245-Drop-Relocated-Groups]]"]
release: ""
related: ["[[PHASE-010-Surface-Ownership]]", "[[FEAT-0046-Plans-On-The-Feature]]", "[[FEAT-0047-Risks-On-The-Issues-Surface]]", "[[FEAT-0048-Changes-On-The-Overview]]", "[[FEAT-0049-Review-Desk-As-Record]]", "[[TASK-0019-Cockpit-Library-And-Pinning]]"]
tests: ["[[TST-0022-Surface-Ownership]]"]
reviewed_by: "model:claude-opus-5"
review_date: "2026-07-30"
review_verdict: "approved"
---

# FEAT-0050 — Library reduction

## Goal

Two of the groups are removable today because they never earned a place; five are removable only after [[FEAT-0046]]..[[FEAT-0049]] land. Splitting them that way keeps every commit reachable.

**Removable on their own merits:**

- **Design** — points at the same `~design/<id>` URLs the Design mode does. [[TASK-0212]] added it before [[FEAT-0043]] existed.
- **Decisions** — the overview record column already renders every ADR; `buildRecordDisclosure` holds `sorted.slice(4)` inline rather than linking out, and `proposed` ADRs route separately to the desk. Not a summary of the register — the register.

**Removable once their destination exists:** Plans, Risks, Changes, Tests.

**Relocated:** Workflows join the Docs tree via `DOC_TREE_INLINE_TYPES`, the mechanism references already use.

## Scope

- `LIBRARY_RARE_TYPES` empties; the by-type loop and the `design` group leave `_library_groups`.
- `workflow` joins `DOC_TREE_INLINE_TYPES`; `workflows` leaves `DOC_TREE_EXCLUDED_ROOTS`.
- `_BY_TYPE_SKIP_IN_LIBRARY` keeps skipping the moved types, so auto-discovery does not resurrect them as personal-vault groups.
- `_changes_subgroups` moves to [[FEAT-0048]]'s payload rather than being deleted.

## Out of Scope

- **Removing the Library mode button.** Pinned + Docs tree is a file browser and opening a file by name stays a real need. Whether it earns a strip slot is a separate call, deliberately not bundled into a reachability change.
- Deleting the `plan`/`risk`/`workflow` handling from `index.py`. The types stay first-class; only their Library grouping goes.
- Touching the upstream project-os workflow template.

## Acceptance

- `nav_payload(mode="library")` returns only `pinned` and `docs-tree` group kinds against this corpus.
- Every criterion in [[REQ-0025]] is ticked with evidence before this reaches `done`.
- Workflows appear in the Docs tree under `workflows/`.
- A personal-vault corpus with a `panel`/`character` type still gets its auto-discovered by-type group — the reduction removes canonical-type groups, not the discovery mechanism.

## Links

- Requirement (gate): [[REQ-0025-No-Type-Loses-Its-Surface]]
- Tasks: [[TASK-0243-Drop-Duplicated-Groups]], [[TASK-0244-Workflows-Into-The-Docs-Tree]], [[TASK-0245-Drop-Relocated-Groups]]
- Test: [[TST-0022-Surface-Ownership]]

## Independent review — 2026-07-30, changes-requested

Fresh session, `model:claude-opus-5`, from the notes and the diff for `bed48ea`; no access to the authoring session's reasoning (ADR-0013 — same model family as the author, different context).

**The Decisions group was not a duplicate, and removing it stranded the type.** The Goal's argument is that "the overview record column already renders every ADR; `buildRecordDisclosure` holds `sorted.slice(4)` inline rather than linking out … Not a summary of the register — the register." The function is exactly as described. What feeds it is not. `fillRecordColumn` (`renderer.ts:10520`) builds `adrs` from `fetchRecordNotes('library')`, i.e. `GET /api/cockpit/nav?mode=library` — the very payload this feature empties. Harvested against this repo's corpus: **149 typed items at `bed48ea~1`, including 8 ADRs and 21 tests; 0 at `bed48ea`**, because only `docs-tree` survives and its items carry no `id`. `if (scopedAdrs.length > 0)` therefore never fires and the Decisions card is not built on the project-scope overview.

So the record column was Library's Decisions group, reshaped — not a second copy of it. Post-change, 8 of this repo's 9 ADRs have no navigation route at all (`ADR-0007` shows only transiently in `mode=recent` because it was just edited), and none is in the Cmd+P corpus either: `QUICK_CORPUS_MODES` covers features/tasks/issues/design/library plus the tests register and the changes payload, and no decision reaches any of those. Meanwhile `decisions` remains in `DOC_TREE_EXCLUDED_ROOTS`, justified in its own comment by "the overview record column". This is the ordering failure [[REQ-0025]] was written to gate against, arriving from the one direction the gate did not check.

**A second regression from the same root cause, claimed nowhere.** The overview's `Verification` record card (21 tests → 0) and the attention inbox's `failing`/`ready` test rows in `appendAsyncWaitingRows` (`renderer.ts:5852`) read the same emptied payload. The Verification card is gone from the project overview; the attention rows are latent only because all 22 tests currently pass. The `buildQuickCorpus` near-miss the phase notes record so carefully is the identical failure — `grep -n "fetchRecordNotes\|mode=library"` over `renderer.ts` returns three call sites, and one of the three was fixed.

**What survived refutation.** The reduction mechanics are solid and genuinely guarded. Re-admitting a high-count type to `LIBRARY_RARE_TYPES` fails; gutting the `_BY_TYPE_SKIP_IN_LIBRARY` literal fails two tests; re-adding `workflows` to `DOC_TREE_EXCLUDED_ROOTS` fails; dropping `workflow` from `DOC_TREE_INLINE_TYPES` fails `test_workflows_join_the_docs_tree`. Keeping `LIBRARY_RARE_TYPES` as a named empty tuple with a comment about what not to append to it is the right call. The Design removal is clean — its reachability guard moved to `_design_groups` rather than being deleted with the group, and `test_designs_reach_the_bench_from_the_design_mode` additionally asserts the duplicate route is gone. That is the pattern the Decisions removal needed and did not get.

**To clear this.** Decisions need a destination that survives the reduction (a decisions payload or a register the reduction does not empty), and the same for the overview's Verification card. Then re-tick [[REQ-0025]] criterion 5 against an assertion about the *source* of the record column, not the shape of the function that renders it. This feature should not be `done` until then.
## Re-review — 2026-07-30, approved

The Decisions removal now has what the Design removal had all along: its destination is a payload of its own, not a by-product of the surface being reduced. `GET /api/cockpit/decisions` returns all 8 ADRs (verified over HTTP), `fillRecordColumn` reads it, and `fetchRecordNotes` — the harvest abstraction that made three callers depend on a nav mode's contents — is deleted rather than merely bypassed. Deleting it is the stronger fix and I could not find a remaining caller.

A corpus-wide sweep confirms no canonical type is now unreachable ([[REQ-0025]]). Two limits stay open and are recorded on [[TST-0022]] and [[ISS-0065]] rather than pretended away: the new cross-process contract has no behavioural guard, and the fix's own notes carry two figures I could not reproduce.
