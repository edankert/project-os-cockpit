---
type: "[[task]]"
id: TASK-0015
aliases: ["TASK-0015"]
title: "Cockpit left-pane modes (Features / Tasks / Issues / Recent)"
status: done
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-08
updated: 2026-05-08
source: ["[[CHG-20260508-Cockpit-Left-Modes-And-Palette]]"]
implements: ["[[FEAT-0006]]", "[[REQ-0013]]"]
fixes: []
effort: M
due: ""
depends: ["[[TASK-0013]]"]
blocks: []
related: ["[[REQ-0013]]", "[[TST-0002]]"]
tests: ["[[TST-0002]]"]
---

# TASK-0015 — Cockpit left-pane modes

## Definition of Done
- [x] `/api/cockpit/nav?mode=<features|tasks|issues|recent>` returns the matching mode's payload. Missing/unknown mode falls back to `features`.
- [x] Schema bumped to v2 with a generic group envelope (`{key, label, url, status, items}`) so a single JS renderer covers all four modes. `X-Cockpit-Schema: 2` on every cockpit JSON response.
- [x] **Features** mode: features grouped by phase (existing behaviour preserved), phase status chip right-aligned in the group header.
- [x] **Tasks** mode: tasks grouped by status, ordered by a curated lifecycle (`doing → in-progress → in-review → next → blocked → ready → planned → backlog → triage → ... → done → archived`). Group header carries the status chip. Item subtitle: parent feature ID + ` · ` + effort.
- [x] **Issues** mode: issues grouped by severity (`critical → high → medium → low`, then any extras alphabetically). Item subtitle: affected feature + component.
- [x] **Recent** mode: top 60 notes by `updated` (falls back to `created`), bucketed Today / Yesterday / This week / This month / Earlier. Templates and dashboard notes excluded.
- [x] Mode picker renders as sticky tabs at the top of the left pane. Selected mode persists in `localStorage` under `docs-server.cockpit.left-mode`.
- [x] Each mode keeps its own collapsed-group state (key prefix `nav:<mode>:<group-key>`) so opening a Doing group in Tasks mode doesn't affect the same key in Features mode.
- [x] Tests in `tests/test_cockpit.py` cover: schema versioning, default-mode fallback, group shape per mode, item subtitle content, template exclusion in recent.

## Steps
- [x] Generalise `nav_payload(index, mode)` in `src/docs_server/cockpit.py`; one helper per mode.
- [x] Add `?mode=` parsing to `_serve_cockpit_nav` in `src/docs_server/server.py`.
- [x] Rewrite `renderLeftPane` in `src/docs_server/static/cockpit.js` for the v2 envelope; add `renderModeTabs` + persistence.
- [x] Add `.nav-mode-bar` + `.nav-mode-tab` CSS in `src/docs_server/static/cockpit.css`.
- [x] Extend `tests/fixtures/index_basic/` with two tasks and two issues (covering `doing` + `backlog` statuses, `high` + `low` severities) so the new modes have real input.
- [x] Bump `EXPECTED_SCHEMA` in cockpit.js; preserve graceful-degradation warning on schema mismatch.

## Notes
- Mode picker is in the left pane (not the global header) because the filter scope is "what this pane lists." Hide-completed and theme toggle stay in the global header — they apply across panes.
- The `subtitle` field is mode-specific but the renderer is one function: it just shows whatever string the server provides. Adding a new mode is a server-side change only (define a `_<name>_groups()` function and register it in `NAV_MODES`).
- Tasks `doing` group is empty in this repo's own docs right now (TASK-0014 is `backlog`, TASK-0013 is `done`); verified visually in `../your-trainer` where dozens of doing tasks exist.

Closed by: [[CHG-20260508-Cockpit-Left-Modes-And-Palette]].
