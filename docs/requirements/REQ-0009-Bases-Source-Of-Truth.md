---
type: "[[requirement]]"
id: REQ-0009
aliases: ["REQ-0009"]
title: ".base files are the source of truth for cockpit pane content"
status: retired
implements: ["[[FEAT-0006]]"]
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-07
updated: 2026-05-23
source: []
priority: high
scope: "FEAT-0006"
specifies: ["[[FEAT-0006]]"]
verifies: []
related: ["[[REQ-0010]]", "[[REQ-0011]]"]
tests: []
---

# REQ-0009 — Bases as source of truth

> **Retired (2026-05-08).** Superseded by [[REQ-0013]]. See [[ADR-0004]] for the design pivot from `.base`-driven to code-driven cockpit. `.base` files remain Obsidian dashboards; they are no longer the cockpit's data source.

## Statement
The cockpit's pane content — which notes appear, in what order, with what columns and grouping — SHALL be defined exclusively by `.base` files (Obsidian Bases YAML format) under `docs/__bases__/`. The server SHALL NOT hardcode pane filters, sort orders, or column lists in Python.

Editing a `.base` file SHALL change the rendered cockpit on the next page load (and live, via SSE, when TASK-0011 is in place) — without code changes to project-os-cockpit.

## Acceptance Criteria
- A change to `NAV.base`'s `views[]` (e.g. adding a new tab, renaming a column) is reflected in the cockpit within one page load / SSE roundtrip.
- A new `.base` file dropped into `docs/__bases__/` becomes mountable in either pane via the cockpit CLI flags (REQ-0010) without code changes.
- The evaluator covers every primitive used in the existing 12 `.base` files (catalogued in TASK-0008's DoD); unrecognised primitives degrade gracefully (warn + exclude row), they do not crash the pane.

## Rationale
Edwin maintains the project-os bases as Obsidian dashboards already; the web cockpit must use the same definitions or the two views drift. Hardcoding filters in Python would create exactly that drift.

## Traceability
- Implements: [[FEAT-0006]]
- Verified by: TASK-0008's unit tests against NAV.base + CONTEXT.base + every other `.base` in the repo.
