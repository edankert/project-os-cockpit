---
type: "[[change]]"
id: CHG-20260508-Cockpit-Shell-And-Renderer
aliases: ["CHG-20260508-Cockpit-Shell-And-Renderer"]
title: "Cockpit shell + JS pane renderer; bare-ID frontmatter cleanup"
status: merged
owner: user:edwin
created: 2026-05-08
updated: 2026-05-08
source: ["[[TASK-0013]]"]
commit: ""
pr: ""
impacts:
  - "src/docs_server/templates.py"
  - "src/docs_server/renderer.py"
  - "src/docs_server/static/cockpit.js"
  - "src/docs_server/static/cockpit.css"
  - "src/docs_server/static/base.css"
  - "docs/**/*.md (frontmatter only)"
issues: []
features: ["[[FEAT-0006]]"]
related: ["[[REQ-0012]]", "[[REQ-0013]]", "[[ADR-0004]]", "[[CHG-20260508-Cockpit-Json-Api]]", "[[TASK-0014]]"]
---

# Cockpit shell + JS pane renderer online

## Summary
Every note page is now wrapped in the 3-pane cockpit shell. A vanilla-JS renderer (`cockpit.js`) consumes the JSON API from [[CHG-20260508-Cockpit-Json-Api]] to paint the left (features-by-phase) and right (outbound + inbound-only) panes. Centre-pane navigation is fetch-then-DOM-swap so only the panes that need to change re-render.

This CHG also lands a one-shot cleanup of frontmatter link fields across `docs/`: bare project-os IDs (`related: [FEAT-0001, REQ-0012]`) became Obsidian wikilink form (`related: ["[[FEAT-0001]]", "[[REQ-0012]]"]`) so links are consistent between body markdown and frontmatter and Obsidian renders them correctly.

## Impact

### UI
- Every note URL (`/docs/<rel-path>`) returns the cockpit shell: header (with brand + theme toggle + view-source link), `<aside class="cockpit-pane left">`, `<main class="cockpit-pane centre">` containing the existing renderer output, `<aside class="cockpit-pane right">`. Embedded `<script type="application/json" id="cockpit-config">` carries `{schema_version, active: {id, path, url, title}}` for the JS to read.
- **Left pane** — features grouped by phase. Phase headers show `PHASE-001 · MVP` (id + title) + the phase's own status chip, link to the phase note. Items render as cards: status chip (top-left), `FEAT-XXXX` id (small), title (link to the note), goal underneath (2-line clamp). Whole card is clickable. A sticky "Hide completed" filter pill collapses `done` / `closed` / `verified` / `passing` / `merged` / `published` items; toggle state persists in `localStorage` (`docs-server.cockpit.hide-completed`).
- **Right pane** — relationships grouped per note type, with outbound and inbound-only items merged inside the same type group. Group headers use a type-colored uppercase label (`features` / `tasks` / `requirements` / ...) — text-only, not a chip — so types don't visually compete with status chips. Each item is a 2-line card matching the left pane: status chip + id + (priority if any) on the top line, title on its own line underneath. Inbound-only items follow the outbound items inside a group, separated by a dashed `↩ inbound only` divider, and rendered with muted/italic styling.
- **Collapsible groups** — both panes use `<details>`/`<summary>` for native browser collapse semantics, with a custom CSS chevron. Each group's open/closed state is persisted in `localStorage` under `docs-server.cockpit.collapsed-groups` (a JSON array of keys: `nav:<phase-id>`, `ctx:<type>`). A group closed in one note stays closed when navigating to another.
- **Centre-pane navigation** — clicks on any link inside the cockpit panes are intercepted by a delegated handler. The renderer `fetch`es the target page, parses with `DOMParser`, swaps `<main class="cockpit-pane centre">` and updates `#cockpit-config` to point at the new active note, then re-fetches `/api/cockpit/context?this=<new>`. `history.pushState` keeps the URL honest; `popstate` reverses the swap. The left pane is cached for the session — only re-fetched on SSE invalidation (TASK-0014, next).

### Backend changes
- `src/docs_server/templates.py::page()` gained a `cockpit_active` parameter (`{id, path, url, title}` or `None`). When provided, the body wraps in `.cockpit-shell` chrome and emits `#cockpit-config` + `<script src="/_static/cockpit.js" defer>`. Index pages (auto-generated `/index/<type>` routes) skip the cockpit chrome — they're navigation, not notes.
- `src/docs_server/templates.py::_render_scalar()` now treats bare `<TYPE>-NNNN` IDs (matching `_PROJECT_OS_ID_RE`) as wikilinks during frontmatter rendering — defensive in case any field still ships a bare ID. Real fix is in the data layer (see "Frontmatter cleanup" below).
- `src/docs_server/renderer.py` — note pages now compute `cockpit_active` (id from frontmatter, title, path, url) and pass it through to `templates.page()`.
- `src/docs_server/cockpit.py::nav_payload` — group dicts now also carry `phase_status` (drawn from the phase note's frontmatter) so the JS can render a status chip in the phase header. Schema stays at v1 — additive only. TST-0002 extended with an assertion on the new key.
- `pyproject.toml` — package-data glob `static/*.css` + `static/*.js` already covers the new files; left a clarifying comment.

### Static files
- `src/docs_server/static/cockpit.js` (~390 lines, vanilla, no build): config loader, two pure render functions, fetch+DOMParser nav, hide-completed filter, theme-aware (no inline colors).
- `src/docs_server/static/cockpit.css` (~370 lines): CSS grid 3-column layout (`280px 1fr 320px`), sticky filter bar, card layout for nav items, per-type group headers in the right pane, mobile-narrow collapse to centre-only via `@media (max-width: 900px)`.
- `src/docs_server/static/base.css` extended with type chip color tokens (one per project-os note type) on `:root` and `[data-theme="dark"]`. All ≤60% saturation in HSL.

### Frontmatter cleanup (one-shot)
- 24 `docs/**/*.md` files had bare project-os IDs in `related` / `depends` / `blocks` / `specifies` etc. (e.g. `related: [FEAT-0001, REQ-0012]`). Converted to Obsidian wikilink form: `related: ["[[FEAT-0001]]", "[[REQ-0012]]"]`.
- Why: the body markdown and frontmatter were inconsistent — the body always used `[[X]]`, frontmatter sometimes used bare IDs. The cockpit's right pane reads links from both sources, but bare IDs never resolved (they fell through `Index.by_id`'s priority order with no `[[ ]]` fence). Obsidian also surfaces wikilinked frontmatter values as proper links; bare IDs there render as plain text.
- The 4 ADR `deciders: [user:edwin]` fields got re-quoted as `["user:edwin"]` — cosmetically noisy but YAML-equivalent (no behaviour change).
- Templates under `docs/__templates__/` are pristine — placeholder IDs (`FEAT-0000`, `TASK-0000`) intentionally stay bare in templates.

### Verification
- All 25 tests still passing (TST-0001: 12, TST-0002: 13). No test changes needed for the cleanup — Index/cockpit logic was already wikilink-aware.
- Manual browser smoke (this repo's `docs/`):
  - Landing page (`/`) renders cockpit; left pane shows 4 phase groups with all features.
  - Click `FEAT-0001` card → centre pane swaps, URL becomes `/docs/features/render-server/FEAT-0001-Render-Server.md`, right pane re-fetches and shows outbound (REQ-0001..0007) + inbound-only (the changes that reference FEAT-0001 without a back-reference).
  - Toggle "Hide completed" → completed-status items collapse; refresh preserves the toggle state.
  - Theme toggle still works; cockpit chrome respects light/dark.
  - Mobile-narrow viewport (sub-900px) hides the side panes, centre pane fills the width.

## Follow-ups
- [ ] [[TASK-0014]] — SSE-driven re-fetch: when the file watcher fires, JS invalidates the nav cache and re-fetches the affected pane(s) without a full page reload.
- [ ] If a future use case needs more right-pane columns (effort / phase), bump `SCHEMA_VERSION` to 2 and update `cockpit.js` to negotiate.
