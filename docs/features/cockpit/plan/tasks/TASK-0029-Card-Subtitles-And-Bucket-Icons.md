---
type: "[[task]]"
id: TASK-0029
aliases: ["TASK-0029"]
title: "Cockpit: vertical-centre group icons; tasks/issues subtitles use body description; references show parent dir; per-status/severity/bucket icons"
status: done
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-09
updated: 2026-05-09
source: []
implements: ["[[FEAT-0006]]", "[[REQ-0012]]"]
fixes: []
effort: M
due: ""
depends: ["[[TASK-0028]]"]
blocks: []
related: ["[[TASK-0026]]"]
tests: ["[[TST-0002]]"]
---

# TASK-0029 — Card subtitles + bucket icons

## Definition of Done
- [x] Group-header icons centre vertically with the (uppercase) header text — `align-items: center` on `.nav-group-header .group-header-inner` (was `baseline`).
- [x] Tasks card subtitle is the first paragraph of body text (with wikilinks/markdown stripped, 220-char clamp). Falls to empty when no body.
- [x] Issues card subtitle is the first paragraph of body text — captures `## Problem` content for project-os issue notes.
- [x] References render with title row dropped and parent directory shown as a mono subtitle (e.g. `decisions/`).
- [x] Tasks group icons (`list-checks`) recolour by status via `data-status` (mirrors the existing `--status-*` palette).
- [x] Issues group icons (`alert-octagon`) recolour by severity via `data-severity` (new `--severity-{critical,high,medium,low}` tokens added to base.css).
- [x] Recent group icons are distinct per bucket: today→sun, yesterday→moon, week→calendar-days, month→calendar, earlier→history.
- [x] Tests updated; suite passes.

## Steps
- [x] Added `_first_body_paragraph(body)` helper in `cockpit.py` — skips leading H1 and `##` section headings, collects the first paragraph, strips wikilinks/markdown, clamps at 220 chars.
- [x] `_task_item` and `_issue_item` use the helper for `subtitle`.
- [x] `_reference_item` switched to `title=""` + `subtitle=parent_dir`.
- [x] Added `alert_octagon`, `sun`, `moon`, `calendar_days`, `calendar`, `history` paths to `GROUP_ICONS`; `RECENT_BUCKET_ICONS` table maps bucket key → icon.
- [x] `groupIcon(mode, group)` adds `data-status` (tasks) / `data-severity` (issues) and routes recent buckets to per-key icons.
- [x] `navItemStacked` renders an optional `.nav-subtitle-stacked` row for references' parent dir.
- [x] CSS: `.group-icon[data-status=...]` mapped to `--status-*`; `.group-icon[data-severity=...]` mapped to new `--severity-*` tokens.
- [x] base.css: 4 severity tokens for light + dark themes.
- [x] Tests rewritten: tasks/issues subtitle assertions check body-description shape; references test asserts parent-dir subtitle for files under `tests/`.

## Notes
The body-description heuristic stops at the next blank line or `##` heading, which means tasks whose body starts with a checklist or blockquote will surface that line. Acceptable v1 — refining the description-extraction is a follow-up if any reads as noise.
