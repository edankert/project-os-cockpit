---
type: "[[change]]"
id: CHG-20260509-Cockpit-Card-Subtitles-And-Bucket-Icons
aliases: ["CHG-20260509-Cockpit-Card-Subtitles-And-Bucket-Icons"]
title: "Cockpit: card-subtitle rework (body descriptions for tasks/issues, parent dir for references), per-status/severity/bucket group icons, vertical-centred icons"
status: merged
owner: user:edwin
created: 2026-05-09
updated: 2026-05-09
source: ["[[TASK-0029]]"]
commit: ""
pr: ""
impacts:
  - "src/project_os_cockpit/cockpit.py"
  - "src/project_os_cockpit/static/cockpit.js"
  - "src/project_os_cockpit/static/cockpit.css"
  - "src/project_os_cockpit/static/base.css"
  - "tests/test_cockpit.py"
issues: []
features: ["[[FEAT-0006]]"]
related: ["[[REQ-0012]]", "[[CHG-20260509-Cockpit-Stacked-Items-Right-Pane-Order-And-Group-Icons]]"]
---

# Cockpit: body-description subtitles + per-bucket group icons

## Summary
After eyeballing `your-trainer/docs` in the browser, four refinements:

1. **Vertical alignment** — `.nav-group-header .group-header-inner` was on `align-items: baseline`, which floated SVG icons above the uppercase text. Switched to `center`.
2. **Tasks / Issues subtitles are body descriptions.** New `_first_body_paragraph` helper skips the H1 and any leading `##` heading (so issue cards surface the `## Problem` paragraph), strips wikilinks + inline markdown, clamps at 220 chars. The `parent · effort` and `affects · component` redactions are gone — that information is in the active note's frontmatter when you click in.
3. **References cards** — the title row is dropped (filename in the id slot is identifying enough); the parent directory is shown as a mono subtitle (`decisions/`, `changes/`...).
4. **Group icons** — task buckets recolour by status, issue severity buckets recolour by severity (new `--severity-*` tokens), recent buckets use distinct shapes (today→sun, yesterday→moon, week→calendar-days, month→calendar, earlier→history).

## Impact

### `cockpit.py`
- New `_first_body_paragraph(body, max_chars=220)` — paragraph-extractor with wikilink + inline-markdown stripping (regex-based; not a full parser).
- `_task_item.subtitle` and `_issue_item.subtitle` now call it (over the existing `parent · effort` / `affects · component` strings).
- `_reference_item` simplified — `title=""`, `subtitle=parent_dir` (or `""` for at-root references). The duplicate-title-suppression logic was dropped along with the title row.
- New regex constants (`_HEADING_RE`, `_WIKILINK_RE`, `_MD_LINK_RE`, `_INLINE_FMT_RE`).

### `cockpit.js`
- `GROUP_ICONS` gained `alert_octagon`, `sun`, `moon`, `calendar_days`, `calendar`, `history`.
- New `RECENT_BUCKET_ICONS` table maps bucket key (`today`/`yesterday`/`week`/`month`/`earlier`) → icon paths.
- `groupIcon(mode, group)` rewritten:
  - tasks → `list-checks` + `data-status=<key>` for status-bucket recolouring.
  - issues → `alert-octagon` + `data-severity=<key>` for severity recolouring.
  - recent → per-bucket icon.
- `navItemStacked` appends an optional subtitle paragraph (uses the existing `.nav-subtitle-stacked` styling).

### `cockpit.css`
- `.nav-group-header .group-header-inner` and the standalone `.group-header-inner` rule both now use `align-items: center`.
- `.group-icon` no longer needs the `vertical-align: -2px` hack — the parent flex now centres it.
- New `.group-icon[data-status=...]` rules mirroring the 6-bucket status palette.
- New `.group-icon[data-severity=...]` rules.

### `base.css`
- 4 new severity tokens (`--severity-critical`, `--severity-high`, `--severity-medium`, `--severity-low`) for light + dark themes.

### Tests
- `test_nav_payload_tasks_item_subtitle_carries_parent` → renamed to `..._is_body_description`. Asserts the body-derived subtitle contains `FEAT-0001` (the task fixture body says "Implements [[FEAT-0001]].") and that wikilink markup is stripped.
- `test_nav_payload_issues_item_subtitle_has_affects_and_component` → renamed to `..._is_body_description`. The fixture's ISS-0001 has only an H1, so the subtitle is the empty string — that's the contract.
- `test_nav_payload_library_references_show_filename_in_id_slot` updated: title row is now always empty, subtitle is parent dir for sub-folder refs (`tests/ACCEPTANCE_TESTS.md` → `tests/`) or empty for at-root refs (`README.md` → `""`).

### Verified live (your-trainer/docs)
- Tasks `doing` group: subtitle of TASK-0362 reads "- [x] Shared TestDatabaseFixture + Fixtures harness under android/app/src/...".
- Issues `critical` group: subtitle of "Strava Shows Connected on Website but App Shows 'Not Connected'" reads "After completing the OAuth flow (browser → Strava login → authorize → server redirect → app)...".
- References show entries like `id="ARCHITECTURE.md", title="", subtitle=""` (at root) and `id="README.md", title="", subtitle="changes/"` (in a subdir).

## Follow-ups
- [ ] Body-paragraph heuristic falls into bullet lists / blockquotes when those start the body. Tolerable v1; consider a more refined extractor (skip leading `>`/`-` lines until prose) if it reads as noise.
- [ ] No icons for non-canonical task statuses (anything not in the curated palette). They fall to `--text-muted`. Add to the rule set as new statuses crop up.
- [ ] Consider applying the same body-description heuristic to right-pane ctxItems — would make the right pane more scannable, at the cost of payload size.

## Documentation Coverage (All Types Considered)
- features: not-applicable
- requirements: not-applicable
- tasks: new ([[TASK-0029]])
- issues: not-applicable
- tests: updated (`tests/test_cockpit.py`)
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new (this note)
- snapshot: updated (TASK 28→29, focus.task → TASK-0029, metrics tasks_total 28→29 / tasks_done 22→23, items.changes addition)
