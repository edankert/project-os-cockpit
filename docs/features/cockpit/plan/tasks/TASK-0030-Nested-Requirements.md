---
type: "[[task]]"
id: TASK-0030
aliases: ["TASK-0030"]
title: "Cockpit: requirements nested under features (collapsed by default) + 'Unattached requirements' fallback"
status: done
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-09
updated: 2026-05-09
source: []
parent: "[[FEAT-0006]]"
fixes: []
effort: M
due: ""
depends: []
blocks: []
related: []
tests: ["[[TST-0002]]"]
---

# TASK-0030 — Nested requirements under features

## Definition of Done
- [x] Each feature item in Features-mode payload carries a `children` array of requirement items when at least one requirement specifies it (via `specifies` or `scope` frontmatter).
- [x] Requirements with no resolvable feature link surface in a final `Unattached requirements` group at the bottom of Features mode.
- [x] JS renders `item.children` as a `<details>` collapsible under the feature card. Default state: collapsed; user-opened state persists across reloads.
- [x] Nested item card uses a compact stacked layout (icon + id + title clamp + status), 30px left indent, single-line title with ellipsis.
- [x] Tests assert child attachment + orphan group + lifecycle.

## Steps
- [x] Added `_requirement_feature_ids(index, record)` — resolves `specifies` / `scope` to canonical feature IDs via `index.by_id`.
- [x] Added `_requirement_child_item(index, record)` — compact item shape (id, title, status, type, url).
- [x] Updated `_features_groups`: builds `reqs_by_feature` map, attaches `children` to each feature item, appends `unattached-reqs` group when orphans exist.
- [x] JS `navItem` detects `item.children` and emits a sibling `<details class="nav-item-children">` after the card.
- [x] JS `renderItemChildren` + `navItemNested` — collapsed-by-default storage uses an "open" key in the existing collapsed-set localStorage.
- [x] CSS `.nav-item-children` + `.nav-item-nested` rules — dashed top border, mono toggle row, indented child rows.
- [x] Tests: 3 new cases — exclusion guard for the orphan group, child-attachment assertion for FEAT-0001, orphan-group fixture.

## Notes
The "open" state mirror reuses the existing `collapsed` localStorage map so we don't ship a second persistence mechanism. Means the COLLAPSED storage now holds two semantically different kinds of keys: `nav:<mode>:<group-key>` (close-when-stored) and `nav:item-children-open:<id>` (open-when-stored). Internal-only, no migration risk, but worth keeping in mind if the storage gets serialised elsewhere.
