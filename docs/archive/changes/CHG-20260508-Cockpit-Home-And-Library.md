---
type: "[[change]]"
id: CHG-20260508-Cockpit-Home-And-Library
aliases: ["CHG-20260508-Cockpit-Home-And-Library"]
title: "Cockpit landing (root → cockpit shell + SNAPSHOT-driven home) and Library mode + pin button"
status: merged
owner: user:edwin
created: 2026-05-08
updated: 2026-05-08
source: ["[[TASK-0018]]", "[[TASK-0019]]"]
commit: ""
pr: ""
impacts:
  - "src/docs_server/cockpit.py"
  - "src/docs_server/server.py"
  - "src/docs_server/templates.py"
  - "src/docs_server/renderer.py"
  - "src/docs_server/static/cockpit.js"
  - "src/docs_server/static/cockpit.css"
  - "tests/test_cockpit.py"
  - "tests/fixtures/index_basic/"
issues: []
features: ["[[FEAT-0006]]"]
related: ["[[REQ-0015]]", "[[REQ-0016]]", "[[REQ-0013]]"]
---

# Cockpit landing + Library mode + pinning

## Summary
Three coupled changes. First, the root URL `/` now renders the cockpit shell with a synthesised home page derived from `SNAPSHOT.yaml` (focus block, phase progress, at-a-glance counts, recent changes), falling back to README and then to a minimal type-counts summary. Second, the left pane gains a fifth mode, **Library**, that surfaces every note that wasn't reachable through Features/Tasks/Issues/Recent — orienting docs (README, ARCHITECTURE, etc.), curated docs in canonical subdirs (`tests/ACCEPTANCE_TESTS.md` and friends), and per-type lists for the rare types (ADRs, Releases, Risks, Tests, Workflows, Plans). Third, the page header was restructured into two rows: Row 1 holds the global controls that should never shift (home icon + mode tabs + platform/filter/theme), Row 2 holds the per-page chrome (pin star + breadcrumb) and is hidden entirely on the synthetic landing. The "docs-server" brand moved from the header to a footer at the bottom-right, alongside the version string. A pin button next to the breadcrumb lets the user add any note to the Library's Pinned section, persisted in `localStorage`.

## Impact

### Landing page (REQ-0015)
- `GET /` now returns the cockpit HTML shell with `cockpit_active = {}` (no active note). The JS client mounts left/right panes and the header controls correctly.
- Centre pane on `/` renders the synthesised home in priority order:
  1. **SNAPSHOT-driven** when `SNAPSHOT.yaml` exists at the project root: project header, focus rows (phase / feature / task / issue with status chips), phase progress (each phase + status chip + count of features in that phase, computed from the index so historical phases get accurate counts), at-a-glance metrics (features done/total, tasks done/total, tests passing, issues open, risks open, releases, decisions), recent changes (top 5 from `items.changes`), and a browse-by-type fallback at the bottom for non-zero indexes.
  2. **README fallback** (renders just the body — no second header) when there's no snapshot.
  3. **Minimal summary** (type-count list) when neither exists. No 500 path.
- Right pane shows the existing empty-state ("No active note selected.") when `active.path` is empty. The pin button in the header is hidden on `/` (its slot is `:empty`-driven).
- New helper `_feature_count_by_phase(index)` in `server.py` walks the live index instead of the snapshot, so completed-and-pruned features still count toward their original phase.
- New helper `render_markdown_body(path)` in `renderer.py` returns just the body HTML (no `page()` chrome), used by the README fallback so we don't double-wrap the page.

### Two-row header + footer (REQ-0013 amendment, REQ-0015)
- Page header is now a flex column with two rows.
  - **Row 1** (always visible, never shifts): home icon (`⌂`, link to `/`) → mode tabs (Library / Features / Tasks / Issues / Recent) → platform pills → "Hide completed" pill → theme toggle. Library is the first tab — it's the orienting mode and the natural starting point.
  - **Row 2** (only on note pages): pin star → breadcrumb. Hidden via `.is-empty` + `display:none` on the synthetic landing and any non-cockpit page.
- The "docs-server" wordmark moved from the header to a `<footer>` at the bottom-right of the viewport, paired with the version string read from `docs_server.__version__` (currently `v0.1.0`). Footer is small, muted, identifying.
- Body becomes a flex column (`min-height: 100vh`) so the cockpit fills the viewport between header and footer; old fixed `calc(100vh - 41px)` height on `.cockpit` removed in favour of `flex: 1 1 auto`.
- The mode tabs were previously sticky at the top of the left pane, where they were pushed under the centre pane's left border on tight viewports (5 tabs in a 280px column). Moving them to Row 1 of the header gives them ~600px of horizontal room — pill-shaped, never clipped, never jumpy.
- Breadcrumb refresh on client-side navigation: `navigateTo` now swaps Row 2's `class` and breadcrumb `innerHTML` from the freshly-fetched HTML, so the path always reflects the current active note (previously stale after fetch+swap).

### Library mode + pinning (REQ-0016)
- New mode `library` registered in `NAV_MODES`. Selectable from the left-pane mode tabs. Persists like other modes in `localStorage`.
- Three sections, in order:
  - **Pinned** — built from `?pinned=path1,path2,...` (comma-separated). Server resolves each path; non-existent paths are silently dropped. Section omitted when empty or no resolvable pins.
  - **Project handles (top-level)** — every `*.md` directly under `docs/` whose filename doesn't match the project-os ID prefix regex (`^(?:FEAT|TASK|REQ|CHG|ADR|RISK|REL|PHASE|TST|ISS|PLAN|WF)-\d`). One collapsible group, compact filename-only rows.
  - **Project handles (per-subdir)** — one collapsible group per subdirectory that contains non-ID-prefixed `*.md` files at depth ≤ 1. Discovery is auto — any subdir qualifies, no allow-list per project. Excluded by name: `dashboards/` (typically `.base` views, navigator noise) and per-directory `README.md` files (descriptors, not navigation targets). `__bases__/` and `__templates__/` are filtered upstream at the index level. Group label is the directory name (`tests/`); rows show filenames only. Each subdir group has its own collapse state, persisted independently. Files deeper than one level (e.g. `features/<feat>/plan/PLAN.md`) are not surfaced here — pin them if quick access is wanted.
  - **By type — rare** — per-type collapsible groups for `adr`, `release`, `risk`, `test`, `workflow`, `plan`. Each group renders only when at least one note of that type exists. Items use a "stacked" layout (status chip + id on the top line, title on a second line — same shape as the right pane's relationship items) and **drop the type subtitle** — the group header already says "Decisions" / "Risks" / etc., so repeating "adr" / "risk" on every row was noise.
- New JS state: `loadPinned()` / `savePinned()` / `isPinned()` / `togglePinned()`, persisted under `docs-server.cockpit.pinned-paths` (JSON array of docs-root-relative paths).
- New JS helper `mountPinButton()` renders a star button into `#cockpit-pin-slot` (added to the page header). Filled when pinned, hollow otherwise. Pressing it toggles localStorage and, if Library mode is currently visible, drops the nav cache and re-fetches so the change is immediate.
- The pin slot is `:empty`-hidden, so the button doesn't appear on the synthetic landing or non-cockpit pages.
- `setActiveFromUrl` updated: only docs URLs map to an active path; `/` and other non-docs paths set `active.path = ""` so the pin button correctly hides on the landing.
- `loadLeftPane` keys its cache on `(mode, platform, pinKey)` so pinning/unpinning a note while in Library mode triggers a fresh fetch.

### API
- `GET /api/cockpit/nav?mode=library&pinned=<paths>` — schema unchanged at v2, additive. Item shape is the standard `{id, title, status, url, subtitle}` (subtitle = note type so the Library shows the type label inline).

### Tests
- `tests/fixtures/index_basic/README.md` — top-level handle so the discovery rule has something to find.
- `tests/fixtures/index_basic/tests/ACCEPTANCE_TESTS.md` — canonical-subdir handle.
- 4 new test cases (`test_nav_payload_library_includes_handles_section`, `test_nav_payload_library_excludes_id_prefixed_files_from_handles`, `test_nav_payload_library_pinned_section_resolves_paths`, `test_nav_payload_library_pinned_drops_stale_paths`).
- 41 cases passing in 0.25s (was 37; +4).

### Verified
- `:8766/` — landing now shows the cockpit shell with the home block: `Active focus` (phase / feature / task), `Phase progress` (PHASE-001 done · 2 features, PHASE-002 active · 2, PHASE-003 backlog · 1, PHASE-004 backlog · 1), `At a glance` (counts grid), and recent changes. Library mode shows 21 handles + 4 ADRs + 3 risks + 2 tests + 3 workflows + 1 plan.
- `:8767/` — your-trainer landing renders snapshot-driven home; Library mode shows 27 handles + 5 ADRs + 7 releases + 4 risks + 9 tests, etc. Includes `tests/ACCEPTANCE_TESTS.md` and `tests/ACCEPTANCE_RUN_PLAN.md` as expected.
- Pin button: appears on every note page, not on `/`. Toggling persists across reloads. Library mode immediately re-renders to show the new pinned section.

## Follow-ups
- [ ] [[TASK-0014]] — SSE-driven nav re-fetch: when watcher events fire, the nav cache (including the pin-key in the cache key) needs invalidation so the home and Library reflect filesystem changes without a manual refresh.
- [ ] If a project starts using the `references/` or `samples/` subdir for non-curated content, the auto-discovery may surface noise. The fix is a project-os convention (use ID prefixes for typed notes, leave caps-name docs only for curated handles), not a docs-server config knob.
- [ ] The Library's "rare types" set is currently hardcoded. If a project adopts `glossary` or another non-standard type with multiple notes, it won't appear. Could be data-driven later (any type with notes that isn't featured/task/issue and has > N entries).
