---
type: "[[change]]"
id: CHG-20260507-Auto-Index-Pages
aliases: ["CHG-20260507-Auto-Index-Pages"]
title: "Auto-index pages (/index/<type>) + landing page with focus + FEAT-0001 done"
status: merged
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
source: ["[[TASK-0004]]"]
commit: ""
pr: ""
impacts:
  - "src/docs_server/index.py"
  - "src/docs_server/server.py"
  - "src/docs_server/templates.py"
  - "src/docs_server/static/base.css"
issues: []
features: ["[[FEAT-0001]]"]
related: ["[[REQ-0007]]", "[[CHG-20260507-Wikilink-Resolver]]"]
---

# Auto-index pages

## Summary
docs-server now has a real landing page and 11 auto-generated index pages. `/` shows the docs root name, the current `focus.*` from `SNAPSHOT.yaml` (with wikilinks resolved), and a list of all indexable types with note counts. `/index/<plural>` shows the notes of one type, grouped by status, ordered active → backlog → done → closed via `STATUS_RANK`. Groups are HTML5 `<details>`/`<summary>` (collapsible, no JS); done/closed groups default-collapsed.

This change also marks **FEAT-0001 as complete** — all four acceptance criteria from the feature note are satisfied across TASK-0001 through TASK-0004.

## Impact

### New URLs
- `GET /` — landing (was: 302 → `/docs/`). Lists all 11 index types with counts; surfaces `focus.task`, `focus.feature`, `focus.phase` from `SNAPSHOT.yaml`. Wikilinks in focus values (e.g. `[[PHASE-001-MVP]]`) resolve.
- `GET /index/{features,tasks,requirements,issues,risks,decisions,changes,releases,workflows,tests,phases}` — typed index pages.
- `GET /index/{notarealtype}` → 404.
- `GET /index` and `/index/` → 302 to `/`.
- `GET /docs/` continues to be the filesystem listing (unchanged).

### Type → URL mapping
The plural→singular map lives in `INDEX_TYPE_PLURALS` (`server.py`). Notable: `/index/decisions` maps to `type: [[adr]]` because the project-os taxonomy uses `adr` as the canonical type even though the directory is `decisions/`.

### Index behaviour
- Templates under `__templates__/` are excluded from index lists (their placeholder IDs like `FEAT-0000` would inflate counts and confuse browsing). They remain indexed for wikilink resolution.
- Status grouping uses `STATUS_RANK` in `templates.py`. Groups within a type are sorted: active (10s) → backlog (30s) → default (50) → done (60s) → closed/blocked (80s+). Notes within a group are sorted by `note_id`, then `title`.
- Done/closed/obsolete groups default to collapsed; everything else default to open. The user can toggle via the native `<details>` chevron.

### CSS
- New: `.index-group`, `.index-items`, `.index-id`, `.muted-count`, `.meta-heading` and the rotating chevron on `<details>` summaries.
- All token-driven; no hard-coded colors. Dark theme works without separate rules per [[REQ-0012]].

## Follow-ups
- [ ] [[TASK-0005]] — file watcher (FEAT-0002): when it lands, `Index.update_path(...)` should be called on `.md` change events to keep counts/groupings live. Landing/index pages will then reflect filesystem state without a server restart.
- [ ] FEAT-0001 done — consider retro-fitting Tier 1 acceptance `TST-*` notes for the renderer / wikilinks / index pages before/with FEAT-0002.
- [ ] Optional: add `/index/plans` and `/index/dashboards` mappings if those types should be browseable.
