---
type: "[[adr]]"
id: ADR-0004
aliases: ["ADR-0004"]
title: "Cockpit data driver: code-emitted JSON vs `.base` evaluator"
status: accepted
owner: user:edwin
created: 2026-05-08
updated: 2026-05-08
deciders: ["user:edwin"]
related: ["[[FEAT-0006]]", "[[REQ-0013]]", "[[TASK-0012]]", "[[TASK-0013]]", "[[TASK-0014]]"]
---

# ADR-0004 — Cockpit data driver

## Context
FEAT-0006 (3-pane cockpit layout) was originally planned to render its left and right panes by evaluating Obsidian-style `.base` files (YAML query DSL) against the in-memory note index. The motivation was symmetry with Edwin's Obsidian dashboards: edit `NAV.base` once, both Obsidian's cockpit and the web cockpit reflect it.

While scoping the layout in detail, two things became clear:

1. **The web cockpit's preferred layout differs from what bases naturally express.** The left pane is "features grouped by phase, columns = id / title / status / goal" — narrower and more focused than NAV.base's tab set. The right pane is "outbound links + (inbound minus already-outbound), grouped by type, with backlink-only items distinguished" — *richer* than CONTEXT.base, which only covers inbound. The two views serve different purposes, so the symmetry was less valuable than expected.
2. **The right pane semantic isn't expressible in the existing Bases DSL.** Outbound + inbound-difference + visual differentiation requires either a custom predicate or post-processing — at which point the `.base` file is just a thin shell around custom code anyway.

## Decision
The cockpit's left and right panes are driven by **code-emitted JSON** from a dedicated `/api/cockpit/...` endpoint set, not by evaluating `.base` files. The data layer is `Index` (TASK-0007's lookup tables + link graph). The transport contract is JSON; the renderer is vanilla JS in the browser. JSON+JS over server-rendered HTML so future interactive controls (column-sort toggles, filter inputs, graph view) are pure client-side additions.

`.base` files remain in the repo as Obsidian dashboards and are unaffected by this decision — they continue to drive Obsidian's sidebar views.

## Alternatives considered

- **`.base`-driven cockpit (the original plan).** Symmetry with Obsidian, configurable panes via CLI flags, "edit a `.base`, web UI reflects it." Rejected because the web cockpit's preferred layout doesn't actually mirror bases (different pane semantics + columns + grouping); the symmetry was illusory.
- **Server-rendered HTML panes (no JS).** Simpler today, but locks out client-side interactive controls and partial-update navigation. The data layer (Index methods) is identical to the JSON path — switching JSON+JS to server-rendered later is easier than the reverse.
- **Hybrid: code-driven defaults, `.base` overrides.** Adds two layers; if no real `.base` use case appears, the override path is dead weight.

## Consequences

### Positive
- The cockpit layout can be tuned per the project-os use case without contorting it through the Bases DSL.
- The right pane's "outbound + inbound-only-distinguished" view is straightforward in code; would be awkward as a Bases predicate.
- Future interactive UI (sort toggles, filters, a graph pane) is a JS-only change against a frozen JSON contract.
- One source of truth for the cockpit's data layer (the `Index` module) — no parser, no DSL evaluator, no `.base` ↔ JSON translation.
- The `.base` files keep working as Obsidian dashboards. No change for the Obsidian workflow.

### Negative
- Edits to `NAV.base` / `CONTEXT.base` no longer affect the web UI. Two views of the same underlying data, intentionally maintained independently.
- Layout changes require code edits (instead of editing a `.base`). For the current single-user single-layout case this is acceptable; if the cockpit ever needs per-user / per-deployment layout overrides, revisit.

### Deferred
- TASK-0008 (`.base` parser + evaluator), TASK-0009 (`.base` JSON API), TASK-0010 (generic `.base`-mounted cockpit shell), TASK-0011 (cockpit SSE for `.base`-driven panes) — all parked at `status: backlog`, kept in-tree. If a "render any `.base` as a standalone HTML page" use case appears later, those tasks are still ~70% applicable scaffolding.
- REQ-0009 / REQ-0010 / REQ-0011 retired (`.base`-as-source-of-truth, configurable pane mounts, `this.file` re-evaluation). Replaced by the single new REQ-0013 describing the code-driven cockpit's contract.

## Status
Accepted. Reconsider if a real per-deployment cockpit-customisation requirement appears, or if a downstream consumer wants to render its Obsidian bases on the web without going through this codebase.
