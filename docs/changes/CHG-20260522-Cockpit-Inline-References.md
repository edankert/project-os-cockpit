---
type: "[[change]]"
id: CHG-20260522-Cockpit-Inline-References
aliases: ["CHG-20260522-Cockpit-Inline-References"]
title: "Cockpit: references inlined into Docs tree, no rare:reference group"
status: merged
owner: user:edwin
created: 2026-05-22
updated: 2026-05-22
source: ["[[TASK-0036]]"]
commit: ""
pr: ""
impacts:
  - "src/project_os_cockpit/cockpit.py"
  - "src/project_os_cockpit/static/cockpit.js"
  - "src/project_os_cockpit/static/cockpit.css"
  - "tests/test_cockpit.py"
issues: []
features: ["[[FEAT-0006]]"]
related: ["[[CHG-20260509-Cockpit-Library-Refinements]]", "[[CHG-20260509-Cockpit-Item-Layout-Refinements]]"]
---

# Cockpit: inline references

## Summary
References no longer get their own `rare:reference` Library group. They render inline in the Docs tree at their actual filesystem position, carrying the `type: "reference"` flag so the JS picks the book-open icon. Tree rows show the filename only — no status, no id, no type label.

## Impact

### `cockpit.py`
- `LIBRARY_RARE_TYPES` shrunk: `"reference"` removed. The rare-type group loop now iterates `adr / release / risk / test / workflow / plan` only and uses `_rare_item` directly (the `_reference_item` branch is gone).
- New `DOC_TREE_INLINE_TYPES = ("reference",)`.
- `_markdown_tree_group` gains `extra_types: tuple[str, ...] = ()` widening the `untyped_only` filter — typed notes whose type is in the extras set are also accepted.
- `_exclude_from_docs_tree` split into `_excluded_by_prefix` (templates — always applies) and `_excluded_by_root` (canonical subdirs — bypassed for inline-type notes so a reference inside `tests/` or `decisions/` still surfaces).

### `cockpit.js`
- `navItemCompact` prepends `typeIcon(item.type, 12)` when `item.type` is set, and adds `.has-type-icon` to the card class. Untyped rows keep the existing CSS file ::before icon.

### `cockpit.css`
- `.nav-item-compact.has-type-icon::before { content: none; }` — suppresses the default file mask.
- `.nav-item-compact .type-icon { margin-right: 8px; }` — same spacing as the file mask.

### Tests
- `test_nav_payload_library_no_rare_reference_group` — asserts the group is gone.
- `test_nav_payload_library_docs_tree_includes_references` — asserts references at the docs root and inside subgroups (the fixture's `tests/ACCEPTANCE_TESTS.md` lands under a `tests/` subgroup).
- 53 cockpit cases passing / 1 skipped (+1 net).

### Verified live (your-trainer/docs)
- No `rare:reference` group.
- Docs tree root surfaces ARCHITECTURE.md / DESIGN.md / INDEX.md / OWNERSHIP.md / STYLEGUIDE.md (all reference-typed) next to the untyped at-root markdown.
- Subgroups appear for each canonical subdir that contains a reference (changes/README.md, decisions/README.md, …).
- `__templates__/` no longer appears.

## Follow-ups
- [ ] Many canonical subdirs now show a one-item folder containing only their `<dir>/README.md` reference. If that reads as noise, add a tweak to either (a) hide subdirs that contain only README-style notes, or (b) excise README.md from inline-type inclusion.
- [ ] Reference type icon size in the compact row is 12px (matching the file mask). If it reads too small relative to the surrounding text, bump.

## Documentation Coverage (All Types Considered)
- features: not-applicable
- requirements: not-applicable
- tasks: new ([[TASK-0036]])
- issues: not-applicable
- tests: updated (`tests/test_cockpit.py`)
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new (this note)
- snapshot: updated (TASK 35→36, focus.task → TASK-0036, CHG last_date → 20260522, metrics tasks_total 35→36 / tasks_done 29→30, items.changes addition)
