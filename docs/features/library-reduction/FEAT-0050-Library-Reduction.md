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
