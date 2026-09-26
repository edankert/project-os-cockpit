---
type: "[[change]]"
id: CHG-20260508-Cockpit-Platform-Filter
aliases: ["CHG-20260508-Cockpit-Platform-Filter"]
title: "Cockpit platform filter (auto-discovered, picker only when used)"
status: merged
owner: user:edwin
created: 2026-05-08
updated: 2026-05-08
source: ["[[TASK-0013]]"]
commit: ""
pr: ""
impacts:
  - "src/docs_server/cockpit.py"
  - "src/docs_server/server.py"
  - "src/docs_server/templates.py"
  - "src/docs_server/static/cockpit.js"
  - "src/docs_server/static/cockpit.css"
  - "tests/test_cockpit.py"
  - "tests/fixtures/index_basic/"
issues: []
features: ["[[FEAT-0006]]"]
related: ["[[REQ-0013]]", "[[CHG-20260508-Cockpit-Left-Modes-And-Palette]]"]
---

# Cockpit platform filter

## Summary
The cockpit can now filter both panes by `platform` for multi-platform projects (iOS / Android / etc.). The picker auto-discovers from the corpus — projects that don't use the `platform` frontmatter field never see the UI. When iOS is picked, the cockpit keeps iOS-tagged + `shared` + platform-agnostic notes; Android mirrors. "All" disables the filter.

## Impact

### API (additive on schema v2)
- `GET /api/cockpit/nav?mode=...&platform=<value>` — `platform` defaults to `all` (no filter). The payload now carries:
  - `platform` — echoed selection (`"all"` if unset).
  - `available_platforms` — sorted list of distinct non-empty `platform` values found in the corpus (templates excluded). Empty list signals to the JS client "this project doesn't use platform tagging — hide the picker."
- `GET /api/cockpit/context?this=...&platform=<value>` — same platform query param; `linked` and `backlinks` lists are filtered with the same predicate.

### Filter semantics
For a selected platform `P`:

- include records whose own `platform` is `P`, `shared`, or empty/missing
- otherwise drop

So a phase note with no `platform` always passes, a `shared` task always passes, and `platform: ios` records only show under iOS or All. Picking a value that no record carries (e.g. `web` on a project that only tags ios/android) effectively narrows to cross-platform notes.

### UI
- Pill toggle group in the page header, between the breadcrumb and the "Hide completed" filter: `[ All ] [ iOS ] [ Android ]`. Pills reuse the existing chip aesthetic.
- The slot is empty (`display:none` via `:empty`) when `available_platforms` is `[]` — so docs-server's own repo (no `platform` field anywhere) renders the header unchanged.
- Pills are data-driven from `available_platforms`, so a project that introduces `platform: web` later gets a "Web" pill automatically with zero code change. Display labels are title-cased per pill, with explicit overrides for `iOS` / `Android` (preserving the canonical capitalisation).
- Selection persists in `localStorage` under `docs-server.cockpit.platform`. Default `all`.
- If a saved selection points at a platform that no longer exists in the corpus (e.g. the field was removed), the JS silently falls back to `all` rather than rendering an inert pill.

### Verified
- `:8766/` (docs-server's own docs): `available_platforms: []` → picker hidden, header looks identical to before.
- `:8767/` (your-trainer): `available_platforms: ["android", "ios"]` → 3 pills appear. `?platform=ios` returns 34 features (iOS + shared + agnostic); `?platform=android` returns 61; `?platform=all` returns 70 (full corpus).
- 37 unit tests passing in 0.16s — 5 added for `available_platforms` discovery, ios/android filter on tasks, fallback behaviour, and right-pane filtering.

## Follow-ups
- [ ] If the centre pane should warn when the active note is filtered out by the current platform pick (e.g. user is on `TASK-0001 (ios)` with Android selected), surface a soft banner. Skipped for now — the right pane already de-emphasises it via empty groups.
- [ ] Consider showing a small platform indicator on each item card (a tiny "iOS" / "Android" / "Shared" tag) so the user can see at a glance which platform a card is about, especially under "All". Easy add when the demand emerges.
