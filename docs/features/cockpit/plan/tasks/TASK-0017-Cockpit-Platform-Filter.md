---
type: "[[task]]"
id: TASK-0017
aliases: ["TASK-0017"]
title: "Cockpit platform filter (auto-discovered, picker only when used)"
status: done
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-08
updated: 2026-05-08
source: ["[[CHG-20260508-Cockpit-Platform-Filter]]"]
implements: ["[[FEAT-0006]]", "[[REQ-0014]]"]
fixes: []
effort: S
due: ""
depends: ["[[TASK-0015]]"]
blocks: []
related: ["[[REQ-0014]]", "[[REQ-0013]]", "[[TST-0002]]"]
tests: ["[[TST-0002]]"]
---

# TASK-0017 — Cockpit platform filter

## Definition of Done
- [x] `cockpit.py` exposes `available_platforms(index)` returning a sorted list of distinct non-empty `platform` values across real notes (templates excluded).
- [x] `nav_payload(index, mode, platform)` and `context_payload(index, this, platform)` accept a `platform` argument; both filter their items via the shared `_platform_match(record, platform)` predicate.
- [x] Filter semantics: `None` / `"all"` → no filter. Any concrete platform `P` includes records whose own `platform` ∈ `{P, "shared", ""}`.
- [x] `/api/cockpit/nav` and `/api/cockpit/context` accept `?platform=` query param. Echoed in the response as `payload.platform` (`"all"` if unset). Nav payload also carries `available_platforms`.
- [x] JS picker (in `cockpit.js`): pill toggle group mounted in the page header; pills are data-driven from `available_platforms`. Hidden entirely when the list is empty (via CSS `:empty` on `#cockpit-platform-slot`).
- [x] Display labels: `iOS` and `Android` are explicit overrides; everything else title-cased per pill (`web → Web`, `desktop → Desktop`).
- [x] Selection persists in `localStorage` under `docs-server.cockpit.platform`. Default `all`.
- [x] Stale-selection safety: if the saved platform isn't in the current `available_platforms`, fall back silently to `all` (no inert pill).
- [x] Both panes refetch on platform change.
- [x] Tests cover: discovery sort order, iOS-filter on tasks, unknown-platform fallback, right-pane filter, right-pane filter drops other-platform items.

## Steps
- [x] Add `available_platforms()`, `_normalise_platform()`, `_record_platform()`, `_platform_match()` helpers in `src/docs_server/cockpit.py`.
- [x] Thread `platform` through the four `_<mode>_groups()` functions and `_grouped_items()`.
- [x] Add `?platform=` parsing in `src/docs_server/server.py` for both nav and context.
- [x] Add `<div id="cockpit-platform-slot">` to the page header in `src/docs_server/templates.py`.
- [x] Add `mountPlatformBar()`, `loadPlatform()`/`savePlatform()`, `platformLabel()` in `src/docs_server/static/cockpit.js`. Refetch nav + context on pill click.
- [x] Style `.platform-bar` + `.platform-pill` + the `:empty` hiding rule in `src/docs_server/static/cockpit.css`.
- [x] Add `platform` field to two fixture tasks + one issue; write 5 tests in `tests/test_cockpit.py`.

## Notes
- Picker is auto-discovered to satisfy the user requirement that single-platform projects see no header churn. Empty-list signal flows through CSS, not JS — the slot just doesn't render any children, and `:empty` collapses it.
- "All" pill is JS-only — never appears in `available_platforms` (which is the data signal). It's the disable-the-filter affordance.
- The picker renders into a slot that's always present in the page-header HTML. This means non-cockpit pages (landing, index/<plural>) don't get the picker because their header doesn't include the slot div.

Closed by: [[CHG-20260508-Cockpit-Platform-Filter]].
