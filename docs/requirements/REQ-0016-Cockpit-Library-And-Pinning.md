---
type: "[[requirement]]"
id: REQ-0016
aliases: ["REQ-0016"]
title: "Cockpit Library mode + pin button (curated + auto-discovered + rare types)"
status: verified
implements: ["[[FEAT-0006]]"]
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-08
updated: 2026-05-23
source: []
priority: medium
scope: "FEAT-0006"
specifies: ["[[FEAT-0006]]"]
verifies: []
related: ["[[REQ-0013]]", "[[TASK-0019]]"]
tests: ["[[TST-0002]]"]
---

# REQ-0016 — Cockpit Library mode + pin button

## Statement
The cockpit left pane SHALL gain a fifth mode, **Library**, that surfaces every note that isn't reachable through the existing Features / Tasks / Issues / Recent modes. The page header SHALL gain a **pin button** that toggles the active note's membership in a per-user pin list.

### Library mode — three sections

1. **Pinned** — items the user has explicitly pinned (via the pin button), in pin order. Empty when nothing is pinned. Persisted in `localStorage` under `project-os-cockpit.cockpit.pinned-paths` (JSON array of docs-root-relative paths).

2. **Project handles** — auto-discovered orienting documents. Discovery rule:
   - Every `*.md` directly under `docs/` whose filename does NOT match a project-os ID prefix (`FEAT-/TASK-/REQ-/CHG-/ADR-/RISK-/REL-/PHASE-/TST-/ISS-/PLAN-/WF-`).
   - Plus every non-ID-prefixed `*.md` one level deep in any subdirectory NOT in the exclude list. Default exclude list is `dashboards/` (per project convention dashboards typically hold `.base` views, not orienting docs); `__templates__/` and `__bases__/` are already filtered at the index level.
   - `README.md` files inside subdirs are excluded — they're directory descriptors, not navigation targets.
   - Files deeper than one level (e.g. `features/<feat>/plan/PLAN.md`) are not surfaced as handles — pinning is the affordance for those.
   - Per-subdirectory groups are nested as `subgroups` under the parent "Project handles" group rather than as siblings of the rare-types groups, so the user can collapse the entire handles section in one click. Each subgroup has its own persisted collapse state.

3. **By type — rare** — collapsible per-type groups for note types that exist in the corpus but aren't a primary nav mode: `adr`, `release`, `risk`, `test`, `workflow`, `plan`. Each group renders a compact list (status chip + id + title link) and respects the per-mode collapsed-state persistence (`nav:library:<group-key>`).

### Pin button
- Star icon in the page header, next to the theme toggle.
- Visible only when there is an active note (omitted on the synthetic landing).
- Filled outline when the active note is pinned, hollow outline when not.
- Click toggles pin state for the active note's path; persists to `localStorage`; if Library mode is currently visible, re-renders so the change is immediate.

### API
- `GET /api/cockpit/nav?mode=library&pinned=<comma-separated-paths>` — server resolves each pinned path to a note record (drops paths that no longer exist), then assembles the three sections in the response. Existing `platform=` and unknown-mode-fallback semantics still apply.

## Acceptance Criteria
- Selecting "Library" from the mode tabs lists every top-level project handle (README, INDEX, ARCHITECTURE, DESIGN, GLOSSARY, OWNERSHIP, PHASES, STYLEGUIDE, DASHBOARD, etc. — whatever exists in the docs root that isn't ID-prefixed).
- `tests/ACCEPTANCE_TESTS.md`, `tests/ACCEPTANCE_RUN_PLAN.md`, and similar curated docs in the canonical subdirs appear in the Project handles section.
- ADRs / Releases / Risks / Tests / Workflows / Plans appear under "By type — rare" only when at least one note of that type exists. Empty groups don't render.
- Clicking the pin button on a feature / task / requirement note adds it to the Pinned section; clicking again removes it. State persists across reloads.
- A pinned path that no longer exists in the corpus (file deleted) is silently dropped on the next nav fetch — no inert pinned row.
- Library mode honours the platform filter and "Hide completed" filter the same way the other modes do.

## Rationale
The existing four nav modes only cover ~3 of the ~13 project-os types (features, tasks, issues; plus the time-sliced Recent). ADRs, Releases, Risks, Tests, Workflows, Plans, and curated reference docs (READMEs, design notes, acceptance test plans) are only reachable today via the breadcrumb, the auto-`/index/<plural>` pages, or right-pane backlinks. Library mode is the catch-all so every note is reachable from a single place.

Pinning solves the "I keep coming back to this note" problem without forcing any particular file to be a project-handle. The auto-discovered Project handles section gives every project a reasonable default set on day one; pinning lets a user curate beyond that (e.g. pin the FEAT they're actively working on, or a CHG they're tracking).

The naming-convention discovery rule is intentional: project-os IDs are `<TYPE>-<NNNN>-...`. Anything outside that pattern is, by definition, a curated document rather than a typed item — they belong in Library, not Recent.

## Traceability
- Implements: [[FEAT-0006]]
- Implemented by: [[TASK-0019]]
- Related: [[REQ-0013]] (cockpit layout — header controls section)

## Verification
- 2026-05-23: marked `verified` — Library mode + pin button shipped (TASK-0019, CHG-20260508-Cockpit-Home-And-Library).
