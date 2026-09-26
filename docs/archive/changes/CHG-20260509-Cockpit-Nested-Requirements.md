---
type: "[[change]]"
id: CHG-20260509-Cockpit-Nested-Requirements
aliases: ["CHG-20260509-Cockpit-Nested-Requirements"]
title: "Cockpit: requirements nested under features (collapsed by default) + Unattached fallback"
status: merged
owner: user:edwin
created: 2026-05-09
updated: 2026-05-09
source: ["[[TASK-0030]]"]
commit: ""
pr: ""
impacts:
  - "src/project_os_cockpit/cockpit.py"
  - "src/project_os_cockpit/static/cockpit.js"
  - "src/project_os_cockpit/static/cockpit.css"
  - "tests/test_cockpit.py"
issues: []
features: ["[[FEAT-0006]]"]
related: ["[[REQ-0013]]"]
---

# Cockpit: nested requirements under features

## Summary
Requirements are now reachable from the left pane without a dedicated tab. In Features mode each feature card carries a collapsed `▸ N requirements` summary row; expanding it reveals the requirements that link to that feature via `specifies` (or `scope`). Requirements that don't link to any feature surface in a final `Unattached requirements` group at the bottom of Features mode so they don't silently disappear.

## Impact

### Server (`cockpit.py`)
- `_features_groups` now builds a `reqs_by_feature` map by walking every `requirement`-typed note and resolving its `specifies` + `scope` links via `index.by_id` (the wikilink target may be `[[FEAT-0006]]` or `[[FEAT-0006-Cockpit-Layout]]` — both resolve to the same record). Each feature item gains `children=[REQ items]` when matches exist.
- New helpers: `_requirement_feature_ids(index, record)`, `_requirement_child_item(index, record)`.
- After the per-phase loop, requirements with no resolvable feature link are emitted as a `unattached-reqs` group with `label: "Unattached requirements"`.

### Client JS (`cockpit.js`)
- `navItem` returns a `<li>` containing the existing `<a>` card *and* a sibling `<details class="nav-item-children">` whenever `item.children` is non-empty.
- New `renderItemChildren(item)` — collapsed by default, with persisted open state under `nav:item-children-open:<id>`. Reuses the existing `collapsed` localStorage map but treats this key family as "open if present" (the inverse of the rest of the cockpit's collapse semantics).
- New `navItemNested(item)` — compact stacked card for child rows: icon (12px) + id + status on a top line, single-line title clamp underneath.

### CSS (`cockpit.css`)
- `.nav-item-children` (dashed-top container), `.nav-item-children > summary` (mono `▸ N requirements` toggle, full-width hover), `.nav-children-chevron` (rotated-square chevron — same primitive as group chevrons).
- `.nav-item-nested` and `.nav-title-nested` for the nested req rows. 30px left padding, smaller font, single-line title.

### Tests
- `test_nav_payload_features_excludes_template_features` updated to ignore the new `unattached-reqs` group when collecting feature IDs.
- New `test_nav_payload_features_attaches_requirements_as_children` — asserts FEAT-0001 carries REQ-0001 as a child (the fixture's REQ-0001 specifies FEAT-0001).
- New `test_nav_payload_features_orphan_requirements_group` — synthesises a REQ with no `specifies`/`scope`, asserts it appears in the orphan group while attached reqs stay out of it.
- 35 cockpit cases passing (was 33; +2 net).

### Verified live (your-trainer/docs)
- `curl /api/cockpit/nav?mode=features` returns features with non-empty `children` arrays:
  - FEAT-0001: 1 child (REQ-0001 "Device Connection (US-1)").
  - FEAT-0011: 11 children.
  - FEAT-0010: 6 children.
- No `unattached-reqs` group in your-trainer (every req there is linked).

## Follow-ups
- [ ] Considers only `specifies` and `scope` frontmatter. Requirements that link to features via `related` or freeform body wikilinks won't be surfaced under those features. If that's needed, expand the resolver to walk additional fields.
- [ ] The localStorage map is now polymorphic: some keys mean "collapsed when stored", the new family means "opened when stored". Internal-only, no consumer outside this JS, but worth noting if the map is ever serialised externally.
- [ ] If a feature has many (>20) requirements, the expanded list could dwarf the surrounding cards. Consider a "show all / collapse" affordance or paginated reveal.

## Documentation Coverage (All Types Considered)
- features: not-applicable
- requirements: not-applicable (refinement satisfies REQ-0013's left-pane navigator scope)
- tasks: new ([[TASK-0030]])
- issues: not-applicable
- tests: updated (`tests/test_cockpit.py`)
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new (this note)
- snapshot: updated (TASK 29→30, focus.task → TASK-0030, metrics tasks_total 29→30 / tasks_done 23→24, items.changes addition)
