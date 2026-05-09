---
type: "[[change]]"
id: CHG-20260509-Cockpit-Library-Refinements
aliases: ["CHG-20260509-Cockpit-Library-Refinements"]
title: "Cockpit Library refinements: tree-merged top-level docs, filename-first rare items, type icons, Obsidian-style file tree"
status: merged
owner: user:edwin
created: 2026-05-09
updated: 2026-05-09
source: ["[[TASK-0021]]", "[[TASK-0022]]", "[[TASK-0023]]", "[[TASK-0024]]"]
commit: ""
pr: ""
impacts:
  - "src/project_os_cockpit/cockpit.py"
  - "src/project_os_cockpit/static/cockpit.js"
  - "src/project_os_cockpit/static/cockpit.css"
  - "tests/test_cockpit.py"
issues: []
features: ["[[FEAT-0006]]"]
related: ["[[REQ-0012]]", "[[REQ-0013]]", "[[REQ-0016]]"]
---

# Cockpit Library refinements

## Summary
Four coupled visual / data refinements to Project (Library) mode, agreed via the assistant's option-picker:
1. **Top-level docs merged into Docs tree** — README.md / ROADMAP.md / SECURITY.md surface at the root of the `docs-tree` group instead of as a separate "Top-level docs" section. Single tree, fewer groups, predictable file-tree feel.
2. **Filename-first rare items** — Pinned and rare-type groups (Decisions / Releases / Risks / Tests / Workflows / Plans / References) now render the **filename** as the title and the **parent directory** as a faint mono subtitle. Recognising an ADR by `ADR-0004-Cockpit-Code-Driven-Vs-Bases.md` beats reading "Cockpit data driver: code-emitted JSON vs `.base` evaluator" off the top of a list of similarly-titled ADRs.
3. **Inline SVG type icons** — Lucide-style monochrome stroke icons render next to every item (left and right panes) and group header, keyed by note type and recoloured via the existing `--type-<name>` tokens. Adds visual scannability without breaking the muted greyscale palette (REQ-0012).
4. **Obsidian-style file tree** — `.nav-group-compact` rows now render with folder/file icons (CSS `mask-image` over `currentColor`), indent guides, tighter rows, full-width hover bands, and no inter-row borders — closer to the Obsidian sidebar feel.

## Impact

### Server (`cockpit.py`)
- Removed `_project_support_group`, `_project_support_item`, `_iter_support_markdown`, `_support_title` (helpers for the now-deleted "Top-level docs" group). `PROJECT_SUPPORT_ROOT_FILES` is kept — `server.py` uses it for the project-root file allowlist.
- New `_project_root_tree_items(project_root)` returns item dicts for whichever of README/ROADMAP/SECURITY exist at the project root.
- `_markdown_tree_group` accepts `extra_root_items` — appended into `root["items"]` and sorted with the indexed entries (README still floats to the top via `_sort_tree_group`).
- `_rare_item` now sets `title = record.path.name` and `subtitle = parent_dir + "/"` (or `""` for docs-root files). Pinned + rare types share this shape.
- Every per-mode item shape (`_feature_item`, `_task_item`, `_issue_item`, `_recent_item`, `_tree_item`, `_rare_item`, `_context_item`, `_project_root_tree_items`) emits a `type` field so the JS can render an icon. Untyped items emit `""`.
- Dropped the no-longer-needed `Iterable` import.

### Client JS (`cockpit.js`)
- New `TYPE_ICONS` table + `typeIcon(type, size?)` helper returning a `<svg>` element with stroke-only Lucide-style paths. Default size 14px (13px for ctx group headers). Unknown types fall back to `file-text`.
- `navItem`, `navItemStacked`, `ctxItem` now prepend `typeIcon(item.type)` before the status chip.
- `ctx-type-label` group header wraps an icon + a `<span>` for the plural label.
- `navItemStacked` renders `item.subtitle` as a `.nav-subtitle-stacked` mono line under the title.
- `renderSubgroup` mirrors `--tree-indent` and `data-depth` onto the `<details>` element so CSS can target nested-only subgroups for the indent-guide pseudo.

### CSS (`cockpit.css`)
- `.type-icon` + per-type colour rules keyed off `[data-type]`, reusing the existing `--type-*` tokens.
- `.nav-subtitle-stacked` — mono, 11px, faint, ellipsised single line.
- `--icon-folder` / `--icon-file` data-URL SVGs at `:root`; applied via `mask-image` on the `::before` of `.nav-subgroup-header .group-header-inner` and `.nav-item-compact`. Recoloured via `background-color: currentColor`.
- `.nav-subgroup` got `position: relative` + a `[data-depth]:not([data-depth="0"])::before` indent-guide line.
- Compact rows get tighter padding (3px vertical), no `border-bottom`, full-width hover band.

### API
- Schema version unchanged (still `2`). Additive: every nav + context item now carries a `type` string.
- Library mode no longer surfaces a `project-support` or `handles` / `handles-dir:*` group.

### Tests
- 4 stale legacy tests rewritten:
  - "handles" / "subdir handles" assertions → assertions that those legacy keys are absent.
  - new test that the `docs-tree` group merges project-root files (README/ROADMAP) when a `project_root` is supplied.
  - "rare items drop subtitle" → "rare items use filename + parent-dir subtitle and carry a `type`".
- 2 new tests assert every item across all modes (and on the right pane) carries a `type` field.
- Suite: 45 passed, 1 skipped (was 41 passed; +4 cases, -1 obsolete behaviour).

### Verified
- `curl /api/cockpit/nav?mode=library` against this repo's docs:
  - `docs-tree` group root items: README.md, PHASES.md, ROADMAP.md, SECURITY.md (URLs `/README.md`, `/docs/PHASES.md`, etc.).
  - Rare-type items: `title: "ADR-0001-Custom-Python-Vs-Static-SSG.md"`, `subtitle: "decisions/"`, `type: "adr"`.
- `curl /api/cockpit/context?this=FEAT-0006` confirms `linked` + `backlinks` items carry `type` (e.g. `"type": "task"`).

## Follow-ups
- [ ] Visual verification in a browser at light + dark themes — server-side payload was confirmed but the implementing agent did not open the cockpit in a browser. Worth a manual eyeball on icon weights, indent-guide positioning, and the file/folder mask rendering on Safari + Firefox.
- [ ] If `mask-image` SVG data URLs render unevenly across browsers, fall back to inline SVG `<img>` siblings or `<svg>` elements with `xlink:href` to a defs block.
- [ ] Phase icon path is a placeholder (gantt-bar shape); swap for a proper Lucide milestone glyph if the visual lands flat.

## Documentation Coverage (All Types Considered)
- features: not-applicable (no new feature; refinements under [[FEAT-0006]])
- requirements: not-applicable (no requirement change; refinements satisfy existing REQ-0012/REQ-0013/REQ-0016)
- tasks: new ([[TASK-0021]]..[[TASK-0024]])
- issues: not-applicable
- tests: updated (`tests/test_cockpit.py`)
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new (this note)
- snapshot: updated (counters.TASK 20→24, metrics.tasks_total 20→24, metrics.tasks_done 14→18, focus.task → TASK-0021, focus.feature → FEAT-0006, items.changes additions)
