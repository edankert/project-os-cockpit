---
type: "[[requirement]]"
id: REQ-0013
aliases: ["REQ-0013"]
title: "Code-driven 3-pane cockpit layout (features-by-phase + outbound + inbound-only)"
status: approved
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-08
updated: 2026-05-08
amended: 2026-05-08
source: []
priority: high
scope: "FEAT-0006"
specifies: ["[[FEAT-0006]]"]
verifies: []
related: ["[[ADR-0004]]", "[[REQ-0014]]"]
tests: ["[[TST-0002]]"]
---

# REQ-0013 — Cockpit layout

## Statement
The web cockpit SHALL render three panes whose content and shape are computed by project-os-cockpit in Python (no `.base` evaluator) and delivered to the browser as JSON for client-side rendering. Layout:

### Left pane — project navigator
A picker with **four selectable modes** (sticky tabs at the top of the pane):

1. **Features** *(default)* — features grouped by `phase`. Group headers are wikilinks to the corresponding phase note and carry the phase's own status chip, right-aligned. Item card columns: `status` chip + `id` + `title` (linking to the note) + `goal` underneath (2-line clamp).
2. **Tasks** — tasks grouped by `status`. Group order follows a curated lifecycle (doing → in-progress → blocked → ready → planned → backlog → done → archived). Group header carries a status chip matching the group. Item card subtitle: parent feature ID + ` · ` + effort.
3. **Issues** — issues grouped by `severity` (`critical → high → medium → low`, then any extras alphabetically). Item card subtitle: affected feature + component.
4. **Recent** — top 60 notes by `updated` (falls back to `created`). Bucketed into Today / Yesterday / This week / This month / Earlier. Templates and `dashboard` notes are excluded. Item subtitle: type + ISO date.

Mode is persisted in the browser (`localStorage` key `project-os-cockpit.cockpit.left-mode`); switching is a single fetch, no full-page reload. Each mode keeps its own collapsed-group state (key prefix `nav:<mode>:<group-key>`). Templates under `__templates__/` (placeholder IDs like `FEAT-0000`) are excluded from every mode.

### Centre pane — active note
The selected note rendered exactly as it would render at `/docs/<rel-path>` today. The cockpit just hosts the existing renderer's output.

### Right pane — relationships of the active note
A single per-type-grouped list. Each type group merges outbound and inbound-only items underneath the same type heading, with outbound items first and inbound-only items following beneath a dashed `↩ inbound only` divider, rendered in muted/italic styling.

- **Outbound** — items in `Index.links_from(active)`.
- **Inbound-only** — items in `Index.links_to(active) − Index.links_from(active)` (inbound that aren't already covered by outbound).

For every item, the card layout matches the left pane: `status` chip + `id` + (`priority` if any) on the top line, `title` (rendered as a link to the item's `.md` file) on its own line underneath. `priority` is only meaningful on requirements; rendered as a coloured pill on the right end of the top line.

Type groups are collapsible (`<details>`/`<summary>`) with persisted open/closed state (key `ctx:<type>`). Group headers use a type-coloured uppercase text label (`features` / `tasks` / `requirements` / ...) — text-only, **not** a chip pill, so type indicators don't visually compete with status chips inside the items.

**Right-pane type group order** is fixed and data-driven from an aggregate analysis of a real project-os corpus (~1,200 notes across this repo + `../your-trainer`): the most-frequently-linked types come first, so the typical reader sees the densest relationship sets at the top. The canonical order is:

`task → feature → issue → requirement → change → phase → release → adr → risk → test → workflow → plan → dashboard`

Types absent from this list are slotted alphabetically at the end. Empty type groups (after platform / hide-completed filtering) collapse silently.

### Header controls (cross-cutting)
The page header carries the cockpit-level controls that affect both panes:

- **Mode tabs** at the top of the left pane (Features / Tasks / Issues / Recent), persisted.
- **Platform picker** (only when applicable — see [[REQ-0014]]).
- **"Hide completed" toggle** that filters items in both panes whose status is in either Done bucket (positive: `done`, `merged`, `fixed`, `fulfilled`, `met`, `complete`, `verified`, `passing`, `published`, `closed`; negative: `obsolete`, `retired`, `cancelled`, `superseded`, `wont-fix`, `reverted`). Persisted across sessions.
- **Theme toggle** per [[REQ-0012]].

## Acceptance Criteria
- Pointed at this repo's `docs/`, the cockpit landing renders the **Features** mode left pane with every feature (excluding `__templates__/feature.md`), grouped under phase headers, the phase's own status chip right-aligned in each header, items in card form (status + id + title link + goal).
- Switching to **Tasks** mode regroups by status; **Issues** mode regroups by severity; **Recent** mode shows top 60 by `updated`. Selection persists across reloads.
- Clicking a feature row (or any item card) navigates to that note in the centre pane and triggers a right-pane re-fetch with the new active.
- For an active note that has both outbound links and inbound-only backlinks of the same type, the type group merges them with a `↩ inbound only` divider; inbound items render muted/italic.
- For a type with only outbound or only inbound, the group still renders cleanly without a divider.
- Right-pane type groups appear in the canonical fixed order (`task → feature → …`), regardless of which mode is active in the left pane.
- "Hide completed" hides every item whose status is in either Done bucket, across both panes; toggle state persists.
- Editing a feature note in your editor causes the left pane to re-render (status / goal / phase changes visible) without a full-page reload.
- Editing the active note causes the right pane to re-fetch + re-render in the same way.

## Rationale
The right-pane "outbound + inbound-only" semantics surface both directions of context that matter when reading a project-os note: what the note knows about, AND what knows about the note that the author may not yet be tracking. This is exactly the data the backlink graph from TASK-0007 provides.

The left-pane originally specified only "features-by-phase" because that's how the project-os-cockpit author navigates this repo daily. After dogfooding against `../your-trainer` (1,175 notes), the picker grew to four modes: features-by-phase remains the default browse, but tasks-by-status is the daily-driver execution view, issues-by-severity is the triage view, and recent is the "what changed overnight" view. A more general-purpose nav with arbitrary `.base` definitions was tried and rejected (see [[ADR-0004]]); the four code-defined modes cover the observed daily-use traversals.

The right-pane type ordering was originally an alphabetical-ish guess (`feature, task, requirement, ...`); it was reordered in this amendment based on aggregate link counts in the same `your-trainer` corpus (task: 1,884 links, feature: 1,566, issue: 946, requirement: 671, change: 418, ...). The order is fixed (not context-dependent) so muscle memory works; concrete evidence drives the ranking rather than assumptions about what "should" be relevant.

Merging outbound and inbound-only items under the same type group (rather than two top-level sections) reduces vertical scrolling: when reading a feature, all relevant tasks live in one place rather than being scattered across "Linked from" and "Links back" sections.

See [[ADR-0004]] for the full architectural decision context.

## Traceability
- Implements: [[FEAT-0006]]
- Related: [[ADR-0004]], [[REQ-0014]]
- Verified by: [[TST-0002]] (cockpit JSON API contract — nav modes, context payload, type grouping); manual browser smoke documented in [[TASK-0013]], [[TASK-0015]].
