---
type: "[[change]]"
id: CHG-20260522-Cockpit-Exclude-Canonical-Container-Dirs
aliases: ["CHG-20260522-Cockpit-Exclude-Canonical-Container-Dirs"]
title: "Cockpit: hide all canonical project-os container dirs from the Docs tree"
status: merged
owner: user:edwin
created: 2026-05-22
updated: 2026-05-22
source: ["[[TASK-0037]]"]
commit: ""
pr: ""
impacts:
  - "src/project_os_cockpit/cockpit.py"
  - "tests/test_cockpit.py"
issues: []
features: ["[[FEAT-0006]]"]
related: ["[[CHG-20260522-Cockpit-Inline-References]]"]
---

# Cockpit: hide canonical container dirs from Docs tree

## Summary
Tightens the Docs-tree exclusions so all 12 canonical project-os container dirs disappear from Project mode's tree, including their inline-type contents (e.g. `<dir>/README.md` references). The TASK-0036 bypass that let references inside canonical dirs surface is removed.

## Impact

### `cockpit.py`
- `DOC_TREE_EXCLUDED_ROOTS` extended with `plans`, `releases`, `tasks` (now 12 entries).
- `_markdown_tree_group` filter restored to call `_exclude_from_docs_tree` unconditionally; the inline-type bypass is gone. Inline-type widening still operates on the `untyped_only` check — at-root references continue to surface.
- `__templates__/` continues to be blocked by `_excluded_by_prefix`.

### Tests
- Removed assertion that `tests/ACCEPTANCE_TESTS.md` appears under a `tests/` subgroup.
- New `test_nav_payload_library_docs_tree_excludes_canonical_container_dirs` — iterates over the full canonical set + `__templates__/` and asserts none appear as Docs-tree subgroups.
- 54 cockpit cases passing / 1 skipped.

### Verified live (your-trainer/docs)
- Docs tree subgroups: `['marketing/', 'reference/', 'references/']` — only user-content directories. Was 15 subgroups including every canonical project-os dir.
- Root items unchanged at 14 (project-root files + docs-root references / untyped notes).

## Follow-ups
- [ ] If a project starts using a non-standard container dir (e.g. `adrs/` instead of `decisions/`), the exclusion list will need to learn it. Could be made data-driven from the rare-types set later.
- [ ] References inside canonical dirs (like the project-os repo's own `decisions/README.md` describing the directory) are no longer reachable from the tree. Pin them or move them to a non-canonical location.

## Documentation Coverage (All Types Considered)
- features: not-applicable
- requirements: not-applicable
- tasks: new ([[TASK-0037]])
- issues: not-applicable
- tests: updated (`tests/test_cockpit.py`)
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new (this note)
- snapshot: updated (TASK 36→37, focus.task → TASK-0037, metrics tasks_total 36→37 / tasks_done 30→31, items.changes addition)
