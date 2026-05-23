---
type: "[[task]]"
id: TASK-0036
aliases: ["TASK-0036"]
title: "Cockpit: references inlined into Docs tree (book icon, filename only, no rare:reference group)"
status: done
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-22
updated: 2026-05-23
source: []
implements: ["[[FEAT-0006]]", "[[REQ-0016]]"]
fixes: []
effort: S
due: ""
depends: ["[[TASK-0021]]"]
blocks: ["[[TASK-0037]]"]
related: ["[[TASK-0025]]"]
tests: ["[[TST-0002]]"]
---

# TASK-0036 — Inline references into Docs tree

## Definition of Done
- [x] No `rare:reference` group in the Library payload.
- [x] Reference-typed notes appear in the `docs-tree` group at their actual filesystem position.
- [x] Items carry `type: "reference"` so the JS renders the book-open icon (not the default file mask).
- [x] Tree items show filename only — no status chip, no id slot, no type label.
- [x] `__templates__/` notes still excluded even for inline types.
- [x] Canonical subdirs (decisions/, tests/, ...) are NOT excluded for inline types, so a reference inside one still surfaces.

## Steps
- [x] `LIBRARY_RARE_TYPES` no longer contains "reference"; added `DOC_TREE_INLINE_TYPES = ("reference",)`.
- [x] `_markdown_tree_group` gains `extra_types` param widening the `untyped_only` filter.
- [x] Split `_exclude_from_docs_tree` into `_excluded_by_prefix` (always applies — templates) and `_excluded_by_root` (canonical subdirs — bypassed for inline types).
- [x] `_tree_item` already emitted `type` from a previous task; no change needed there.
- [x] JS `navItemCompact` prepends `typeIcon(item.type, 12)` when type is set and tags the card with `.has-type-icon`.
- [x] CSS suppresses the file ::before mask when `.has-type-icon` is on the compact row; adds 8px margin-right on the inline `.type-icon` for the row.
- [x] Tests: assert no `rare:reference` group; assert references appear in the docs-tree at root and inside subgroups (tests/ACCEPTANCE_TESTS.md case).

## Notes
A side effect: subgroups now appear for every canonical subdir that contains a reference (typically `<dir>/README.md` describing the directory). The user may want to suppress those one-item README folders later; for now the data flows from filesystem layout.
