---
type: "[[change]]"
id: CHG-20260508-Cockpit-Left-Modes-And-Palette
aliases: ["CHG-20260508-Cockpit-Left-Modes-And-Palette"]
title: "Cockpit left-pane modes (features/tasks/issues/recent) + status palette overhaul"
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
  - "src/docs_server/static/cockpit.js"
  - "src/docs_server/static/cockpit.css"
  - "src/docs_server/static/base.css"
  - "tests/test_cockpit.py"
  - "tests/fixtures/index_basic/"
issues: []
features: ["[[FEAT-0006]]"]
related: ["[[REQ-0012]]", "[[REQ-0013]]", "[[CHG-20260508-Cockpit-Shell-And-Renderer]]"]
---

# Cockpit left-pane modes + palette overhaul

## Summary
The left pane is now a navigator picker rather than a single fixed view. Four modes ship: **Features** (current default — features by phase), **Tasks** (by status), **Issues** (by severity), **Recent** (last 60 notes by `updated`). Mode is persisted in `localStorage` and switches without a page reload. Concurrently, the status-chip palette was rebuilt from real-world status vocabulary observed in two corpora (this repo + `../your-trainer`, ~1,200 notes total): 6 perceptual buckets, all ≤60% saturation per [[REQ-0012]], with previously-unmapped statuses (`fulfilled`, `met`, `wont-fix`, `cancelled`, `superseded`, `reverted`, `in-review`, etc.) now coloured semantically.

## Impact

### Cockpit JSON API — schema v2 (additive break)
- `X-Cockpit-Schema: 2` and `payload.schema_version: 2`. The JS client refuses to render an unknown schema version, so older browser tabs need a refresh.
- `GET /api/cockpit/nav?mode=<features|tasks|issues|recent>` — mode picker; missing/unknown mode falls back to `features`.
- Group envelope is now generic across modes: `{key, label, url|null, status|null, items:[...]}`. Items are `{id, title, status, url, subtitle}`. The mode-specific bits (phase id+title, status name, severity name, time bucket) all collapse to `key` + `label`; mode-specific extras (parent feature on a task, severity-affects on an issue, type+date on a recent) ride on `subtitle`.
- Right pane (`/api/cockpit/context`) is unchanged structurally — it just carries `schema_version: 2` now.

### Mode behaviours
- **Features** (default): groups by phase, sorted by phase `order`. Group label is `"<PHASE-ID> · <Phase Title>"`, header is a link to the phase note, the phase's own status chip is **right-aligned** in the header.
- **Tasks**: groups by status, ordered by a curated lifecycle list (doing → in-progress → blocked → ready → planned → backlog → done → archived). Group header carries the status chip. Item subtitle: parent feature ID + ` · ` + effort (when present).
- **Issues**: groups by severity (`critical → high → medium → low`, then any extras alphabetically). Item subtitle: affected feature + component.
- **Recent**: capped at 60 most-recently-updated notes (by `updated`, falling back to `created`), bucketed into Today / Yesterday / This week / This month / Earlier. Templates and `dashboard` notes are excluded. Item subtitle: type + ISO date.

### Status palette (REQ-0012 compliant)
Six buckets replacing eight:

| Bucket | Hue (light / dark) | Statuses |
|---|---|---|
| Active | 140 32% 38 / 60 (green) | active, approved, accepted, ready, doing, in-progress, in-review, next |
| Pending | 220 14% 48 / 65 (cool grey) | planned, backlog, todo, open, pending, draft, proposed, triage |
| Done — positive | 160 28% 38 / 60 (teal-green) | done, merged, fixed, fulfilled, met, complete, verified, passing, published, closed |
| Done — negative | 0 0% 48 / 58 (muted grey) | obsolete, retired, cancelled, superseded, wont-fix, reverted |
| Blocked | 5 48% 46 / 65 (red) | blocked, failing, reopened |
| Reference | 180 24% 40 / 60 (cyan-grey) | reference, deferred |

- **Closed** dissolved into Done-positive (terminal-with-success).
- **In-review** moved to Active (PR-up-awaiting-review is in flight, not "needs sorting").
- **Planned**, **Proposed**, **Draft**, **Triage** previously all collapsed onto the Backlog colour — now share Pending but visibly distinct from the now-dropped "Triage" hue (folded in).
- Done-negative is desaturated grey: terminal-without-success reads quieter than Blocked's red but still legibly archived.

CSS tokens renamed: `--status-doing/verified/backlog/triage/closed` → `--status-active/pending/done/archived/reference`. The `.ctx-priority` rules in cockpit.css were updated to use the new tokens.

### "Hide completed" filter
Now matches both Done buckets: `done, merged, fixed, fulfilled, met, complete, verified, passing, published, closed, obsolete, retired, cancelled, superseded, wont-fix, reverted`. Previously only covered the v1 set.

### UI plumbing
- Mode picker: a sticky tab bar at the top of the left pane (`Features | Tasks | Issues | Recent`). Click rotates through. Selection persists in `localStorage` under `docs-server.cockpit.left-mode`.
- Phase header in Features mode: status chip pushed to the right edge of the header via a flex spacer, so groups read `[chevron] PHASE-001 · MVP                              active`.
- The collapsed-group state key now includes the mode: `nav:<mode>:<group-key>`. Each mode keeps its own collapse state, so opening a Doing group in Tasks mode doesn't collapse the same-keyed group when you switch to Features mode.

### Tests
- `tests/test_cockpit.py` reworked for v2 envelope; 11 nav-related tests now (8 added: tasks/issues/recent shape + subtitle assertions + unknown-mode fallback). Existing context tests unchanged in intent, just carry the v2 schema number.
- Fixture extended with `TASK-0001-First-Task.md` (doing), `TASK-0002-Backlog-Task.md` (backlog), `ISS-0001-High-Severity.md` (high), `ISS-0002-Low-Severity.md` (low) so the new modes have real input. Existing TST-0001 tests still pass.
- 32 tests passing in <0.2s.

### Verified
- This repo's docs/ on `:8766/`: all four modes render; mode tab persists across reloads and across in-pane navigation; phase chip right-aligned.
- `../your-trainer/docs` on `:8767/`: 1,175-note corpus exercises severity values beyond the spec (cosmetic / enhancement / major / minor) — they slot at the end of the issues mode alphabetically as expected. Recent mode shows that 70 notes were updated today.

## Follow-ups
- [ ] [[TASK-0014]] — SSE-driven nav re-fetch: when a watcher event arrives, JS should drop `navCache` so the next fetch picks up edits without a manual refresh. Currently the nav is cached for the session.
- [ ] If a corpus introduces issue severities outside `critical|high|medium|low|cosmetic|enhancement|major|minor`, consider extending `SEVERITY_ORDER` or surfacing the unknown labels with a warning.
- [ ] If status vocabularies grow further, `base.css` adds one line per new alias mapping to an existing bucket — no token rework needed.
