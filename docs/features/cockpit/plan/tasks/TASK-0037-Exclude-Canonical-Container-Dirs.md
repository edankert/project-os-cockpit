---
type: "[[task]]"
id: TASK-0037
aliases: ["TASK-0037"]
title: "Cockpit: hide all canonical project-os container dirs from the Docs tree"
status: done
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-22
updated: 2026-05-22
source: []
implements: ["[[FEAT-0006]]", "[[REQ-0016]]"]
fixes: []
effort: XS
due: ""
depends: ["[[TASK-0036]]"]
blocks: []
related: ["[[TASK-0021]]"]
tests: ["[[TST-0002]]"]
---

# TASK-0037 — Exclude canonical container dirs

## Definition of Done
- [x] `DOC_TREE_EXCLUDED_ROOTS` covers all 12 canonical project-os container dirs: `changes`, `decisions`, `features`, `issues`, `phases`, `plans`, `releases`, `requirements`, `risks`, `tasks`, `tests`, `workflows`.
- [x] The TASK-0036 inline-type bypass on `_excluded_by_root` is removed — references inside these dirs no longer surface in the Docs tree.
- [x] `__templates__/` continues to be excluded via `_excluded_by_prefix` (unchanged).
- [x] User-content dirs (`marketing/`, `reference/`, `references/`, anything custom) still surface.
- [x] Tests cover both the inclusion of at-root references and the exclusion of every canonical dir.

## Steps
- [x] Added `plans`, `releases`, `tasks` to `DOC_TREE_EXCLUDED_ROOTS` (now 12 entries, sorted).
- [x] Replaced the conditional `if not is_extra_type and _excluded_by_root(...)` with the unconditional `_exclude_from_docs_tree` helper.
- [x] Updated tests: dropped the "tests/ subgroup appears" assertion (no longer true); added `test_nav_payload_library_docs_tree_excludes_canonical_container_dirs` that loops through all 12 + `__templates__/` confirming none appear as subgroups.

## Notes
A reference living inside a canonical container dir (e.g. `decisions/README.md`) is now hidden from the tree. To navigate to such a note, the user can:
1. Open the canonical group via Library mode's rare-types section (Decisions / Risks / …).
2. Pin the note to the Pinned section.
3. Move the note into a non-canonical user-content directory.
