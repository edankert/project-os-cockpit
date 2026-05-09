---
type: "[[change]]"
id: CHG-20260509-Cockpit-Stacked-Items-Right-Pane-Order-And-Group-Icons
aliases: ["CHG-20260509-Cockpit-Stacked-Items-Right-Pane-Order-And-Group-Icons"]
title: "Cockpit: stacked default items, canonical right-pane type order on merge, type-aware group icons"
status: merged
owner: user:edwin
created: 2026-05-09
updated: 2026-05-09
source: ["[[TASK-0026]]", "[[TASK-0027]]", "[[TASK-0028]]"]
commit: ""
pr: ""
impacts:
  - "src/project_os_cockpit/static/cockpit.js"
  - "src/project_os_cockpit/static/cockpit.css"
issues: []
features: ["[[FEAT-0006]]"]
related: ["[[REQ-0013]]", "[[REQ-0012]]"]
---

# Cockpit: stacked default items, canonical right-pane order, group icons

## Summary
Three coupled left/right-pane refinements after a visual review on `your-trainer/docs`:

1. **Default nav items become stacked.** Features / Tasks / Issues / Recent items previously crammed `[icon] [id] [title] [status]` onto a single line; they now use three rows — `[icon] [id] [spacer] [status]` on row 1, `[title]` on row 2, `[subtitle]` on row 3 (when present). Long IDs (e.g. CHG- ones) ellipsise in the mono slot.
2. **Right-pane types follow the canonical order.** `mergeContext` in the JS used to keep first-appearance order (linked types first, then any backlink-only types appended), which violated REQ-0013. It now sorts the merged map by `TYPE_RANK` (`task → feature → issue → requirement → change → phase → release → adr → risk → test → workflow → plan → reference`).
3. **Group headers carry an icon.** Library mode rare-type groups reuse the matching type icon; Pinned gets a star; Docs tree gets a folder-tree. Features mode → layers, Tasks → list-checks, Issues → alert-octagon, Recent → clock.

## Impact

### `cockpit.js`
- `navItem` rewritten — three-row card matching `navItemStacked` plus a row-3 subtitle when the server emits one. Renders no empty `<p>` when title or subtitle is blank.
- New `TYPE_ORDER` + `TYPE_RANK` constants mirroring `cockpit.py`.
- `mergeContext` no longer keeps a manual `order` array; it sorts `Object.keys(byType)` by canonical rank, falling back to alpha for unranked types.
- New `GROUP_ICONS` table (star, folder-tree, layers, list-checks, clock) + `makeGroupIconSvg` + `groupIcon(mode, group)` helper.
- `renderLeftPane` prepends `groupIcon(mode, g)` to the header children.

### `cockpit.css`
- `.nav-id` switched from `flex-shrink: 0` to `flex: 0 1 auto; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;` so long IDs ellipsise.
- `.nav-title` is now a row-2 paragraph (block, 2-line clamp, regular weight) — replaces the previous inline-flex span.
- `.nav-item:hover .nav-title` and `.nav-item.is-active .nav-title` consolidated; the duplicate at line ~307 removed.
- New `.group-icon` rule — neutral muted color, flex-shrink 0, `vertical-align: -2px` for visual centering against the uppercase header text.
- `.group-header-inner` switched to `align-items: center` (was `baseline`) so SVG icons sit on the same line as the label.

### Tests
- 46 passing, 1 skipped (no test rewrite needed — none asserted the single-line layout, the merge order at JS level, or the group-header DOM).

### Verified
- `curl /api/cockpit/context?this=FEAT-0001` against `your-trainer/docs` returns linked `[requirement, phase]` and backlinks-only `[feature, issue, change, release]`. Server payload unchanged; the JS merge now reorders to canonical `feature, issue, requirement, change, phase, release`.

## Follow-ups
- [ ] Visual eyeball on group icons across the modes — check that the layers icon for phases and the list-checks for tasks read at a glance, and that the type icons on rare groups don't fight the (uppercase, faint) header text.
- [ ] Tasks-mode group header carries both a list-checks left icon AND a right-aligned status chip with the same status name. The icon is intentional (it marks the section type, not the status), but if it reads as redundant, drop it for tasks/issues.
- [ ] If issue severity groups need to communicate severity via icon colour (red for critical, etc.), that's an additional CSS rule on `.group-icon[data-severity="critical"]`.

## Documentation Coverage (All Types Considered)
- features: not-applicable
- requirements: not-applicable (refinements satisfy existing REQ-0013/REQ-0012)
- tasks: new ([[TASK-0026]], [[TASK-0027]], [[TASK-0028]])
- issues: not-applicable
- tests: not-applicable (no behaviour change at the JSON contract)
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new (this note)
- snapshot: updated (TASK 25→28, focus.task → TASK-0028, metrics tasks_total 25→28 / tasks_done 19→22, items.changes addition)
