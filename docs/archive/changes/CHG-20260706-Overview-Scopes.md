---
type: "[[change]]"
id: CHG-20260706-Overview-Scopes
aliases: ["CHG-20260706-Overview-Scopes"]
title: "Overview scopes — drill-down phase dashboards, pane contract restored, lifecycle fixes"
status: merged
owner: user:edwin
created: 2026-07-06
updated: 2026-07-06
impacts:
  - "src/project_os_cockpit/cockpit.py (stats_payload scope param + exit-criteria parser)"
  - "src/project_os_cockpit/index.py (generation counter)"
  - "src/project_os_cockpit/server.py (stats scope query + payload cache)"
  - "desktop/src/renderer/renderer.ts (scope panes, virtual ~overview history, shared agent fetch)"
  - "desktop/src/renderer/renderer.css"
features: ["[[FEAT-0023-Overview-Scopes]]"]
related: ["[[PHASE-007-Agent-Instrumentation]]", "[[TST-0012]]", "[[CHG-20260705-Agent-Instrumentation]]"]
---

# Overview scopes: select a phase, get its dashboard

## What shipped

**Python.** `stats_payload(index, scope="PHASE-####")` narrows hero, status mix, phases, and activity to one phase — direct `phase:` frontmatter, inheritance via the parent feature, and a `features:`-link fallback for phase-less notes (tests, changes, risks). Scoped payloads carry a `scope` block (id/title/status/rel) and `exit_criteria` parsed from the phase note's Exit Criteria checkboxes; unknown scopes 404. `Index.generation` (bumped on every invalidation) backs a per-scope payload cache in the handler, so file-event refetches of the heaviest endpoint stop re-walking the corpus.

**Renderer — the pane contract restored (mockup option D, chosen 2026-07-06).** In Overview the left pane lists scopes: ⌂ Project plus every phase with a mini progress bar; selecting one renders that scope's dashboard in the centre — breadcrumb header with status chip and "open note ↗", scoped hero, per-feature task-square rows, exit-criteria checklist, phase-filtered activity. The right pane shows a live agent **Now** card (state, prompt, ctx/$/duration, jump-to-terminal, undocumented flag) + needs-input rows on top, then the phase's linked/backlinks context (Project scope: pinned notes). The centre live banner from TASK-0127 is retired — the Now card replaces it.

**Lifecycle fixes** (from the 2026-07-06 review): Overview is a virtual history page (`~overview`, `~overview/PHASE-####`) so back/forward reach the dashboard and restore the exact scope; file-change reloads refresh in place preserving scroll; one debounced `/api/cockpit/state` fetch feeds strip + Now card + sessions (was three per hook event); live durations tick every 30s; the right pane never shows stale note context in Overview.

## Verification

- [[TST-0012]] passing (4 tests: scoping, exit criteria, 404, generation + cache behaviour); full suite 175 passed, 1 skipped; `tsc` + build clean.
- Live check against this repo: `?scope=PHASE-007` → 5 features / 17 tasks / 6 exit criteria / scoped feed; unknown scope → 404.
- Visual pass rides on [[TST-0011]] (checklist step 10).
