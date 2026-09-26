---
type: "[[task]]"
id: TASK-0021
aliases: ["TASK-0021"]
title: "Cockpit: merge top-level docs into Docs tree root"
status: done
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-09
updated: 2026-05-23
source: []
parent: "[[FEAT-0006]]"
fixes: []
effort: S
due: ""
depends: []
blocks: ["[[TASK-0024]]", "[[TASK-0036]]"]
related: ["[[TASK-0019]]"]
tests: ["[[TST-0002]]"]
---

# TASK-0021 — Merge top-level docs into Docs tree root

## Definition of Done
- [x] README.md / ROADMAP.md / SECURITY.md surface as files at the root of the "Docs tree" group in Project (Library) mode.
- [x] The separate "Top-level docs" group is removed; `_project_support_group` is deleted.
- [x] Items render with the filename as title (no leading `/` — root-level position in the tree is enough indication).
- [x] URLs continue to point at `/README.md` etc. — no change to `isInternalNoteLink` semantics.
- [x] Tests pass; cockpit JSON test asserts the merged shape.

## Steps
- [x] Refactored `_markdown_tree_group` (cockpit.py) to accept `extra_root_items` merged into `root["items"]` before sort.
- [x] Dropped the `_project_support_group` call from `_library_groups`; added `_project_root_tree_items(project_root)` helper feeding into the tree group.
- [x] Existing `_sort_tree_group` already places README.md first; no extra logic needed.
- [x] Updated `tests/test_cockpit.py` library tests to assert the new shape.

## Notes
The data shape stays nested-tree-friendly so TASK-0024 (Obsidian-style tree CSS) doesn't fight us.
