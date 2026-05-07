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
source: []
priority: high
scope: "FEAT-0006"
specifies: ["[[FEAT-0006]]"]
verifies: []
related: ["[[ADR-0004]]"]
tests: []
---

# REQ-0013 — Cockpit layout

## Statement
The web cockpit SHALL render three panes whose content and shape are computed by docs-server in Python (no `.base` evaluator) and delivered to the browser as JSON for client-side rendering. Layout:

### Left pane — project navigator
A single table listing every feature in the docs tree, **grouped by `phase`** (group headers are wikilinks to the corresponding phase note). Columns:
- `id` — the feature ID (e.g. `FEAT-0001`).
- `title` — the feature's `title` frontmatter, rendered as a link to its `.md` file (i.e. clicking opens the feature in the centre pane).
- `status` — rendered as a status chip per [[REQ-0012]].
- `goal` — the feature's `goal` frontmatter, truncated if necessary.

Templates under `__templates__/` (placeholder IDs like `FEAT-0000`) are excluded.

### Centre pane — active note
The selected note rendered exactly as it would render at `/docs/<rel-path>` today. The cockpit just hosts the existing renderer's output.

### Right pane — relationships of the active note
Two sections, each grouped by note `type` (features / tasks / requirements / risks / decisions / changes / phases / tests / workflows / issues / releases / plans):

- **Linked from this note** — items in `Index.links_from(active)`.
- **Links back to this note** — items in `Index.links_to(active) − Index.links_from(active)` (i.e. inbound that aren't already covered by outbound). Visually distinguished from the outbound section so the reader sees at a glance that "this thing knows about me even though I don't link back."

For every item in BOTH sections, the columns are:
- `id`
- `title` — rendered as the link to the item's `.md` file.
- `status` — as a status chip.
- `priority` — only meaningful on requirements; render blank elsewhere.

## Acceptance Criteria
- Pointed at this repo's `docs/`, the cockpit landing renders the left pane with every feature (excluding `__templates__/feature.md`), grouped under phase headers (PHASE-001 / PHASE-002 / PHASE-003 / PHASE-004), with the four columns specified above.
- Clicking a feature row navigates to that feature in the centre pane and triggers a right-pane re-fetch.
- For an active note that has both outbound links and inbound-only backlinks, both sections appear in the right pane and the inbound-only items are visually distinguished.
- For a note with no outbound links, the "Linked from" section either omits or shows an empty-state; the "Links back" section still renders if applicable.
- Editing a feature note in your editor causes the left pane to re-render (status / goal / phase changes visible) without a full-page reload.
- Editing the active note causes the right pane to re-fetch + re-render in the same way.

## Rationale
The right-pane "outbound + inbound-only" semantics surface both directions of context that matter when reading a project-os note: what the note knows about, AND what knows about the note that the author may not yet be tracking. This is exactly the data the backlink graph from TASK-0007 provides.

The left pane's narrow scope (features-by-phase) reflects the actual browse pattern: when working on docs-server, you almost always navigate by feature first, then drill into tasks / requirements / changes from the right pane. A more general-purpose nav (NAV.base style with multiple tabs) added complexity without clear daily-use value.

See [[ADR-0004]] for the full architectural decision context.

## Traceability
- Implements: [[FEAT-0006]]
- Related: [[ADR-0004]]
- Verified by: TASK-0014 manual smoke test + a future TST-* note covering the JSON API and the right-pane diff logic.
