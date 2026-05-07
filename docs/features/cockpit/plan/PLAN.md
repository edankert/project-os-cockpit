---
type: "[[plan]]"
id: PLAN-FEAT-0006
title: "Plan: Bases-driven 3-pane cockpit layout"
status: draft
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
implements: ["[[FEAT-0006]]"]
---

# Plan — FEAT-0006 Cockpit Layout

## Delivery sequence
1. **TASK-0007 — Note index + backlink graph.**
   Build the read-only data layer everything else queries. Walks the docs root once, parses frontmatter, builds: `(path → frontmatter+body)`, `(id-alias → path)`, and a reverse-link graph. Owned by `docs_server.index` (the existing stub).
2. **TASK-0008 — `.base` parser + DSL evaluator.**
   YAML load + a small expression evaluator for the ~10 primitives catalogued in the FEAT note. Pure functions over the index built in TASK-0007. Returns row sets and per-row column values. Owned by a new module, `docs_server.bases`.
3. **TASK-0009 — `.base` JSON API.**
   Given the evaluator's output and the `views[]` definition, expose `GET /api/base?path=<base>&this=<active>`. Response is JSON: `{ base: {path, name}, views: [{ name, groupBy, order, sort, columnSize, rowHeight }], rows: [{ id, fields: { ... } }] }`. Pure data — no HTML. Versioned via a `Content-Type: application/vnd.docs-server.base+json; v=1` style header so the JS client can detect schema changes.
4. **TASK-0010 — Cockpit shell + JS pane renderer.**
   The 3-pane HTML layout served by the centre route, plus `src/docs_server/static/cockpit.js` (vanilla JS, no build) that:
   - reads URL state (active note + mounted bases),
   - fetches the JSON API for each side pane,
   - renders tabbed tables honouring groupBy / sort / order / columnSize / rowHeight,
   - intercepts in-pane row clicks to push history state and re-fetch the right pane (no full-page reload).
   CLI flags `--cockpit-left` / `--cockpit-right` (each accepts a `.base` path, comma-separated list for multi-tab, or `none`), defaults to NAV/CONTEXT.
5. **TASK-0011 — Cockpit SSE re-fetch.**
   Hook into FEAT-0002's watcher events. The SSE channel emits `{kind: "frontmatter"|"base"|"body", path}` events. The cockpit JS subscribes and triggers targeted re-fetches:
   - `frontmatter` event on any note → re-fetch any pane whose evaluator could include that note,
   - `base` event on a `.base` path → re-fetch any pane mounting that base,
   - `body` event on the active note → soft-reload only the centre pane.
   Coalesce bursts (≥50ms quiet window) into one re-fetch per pane.

## Dependencies
- **Hard:** FEAT-0001 must be far enough along that there's a working centre-pane renderer to wrap (TASK-0002 + TASK-0003).
- **Hard:** FEAT-0002 must exist for TASK-0011 (cockpit SSE). TASK-0007 / 0008 / 0009 / 0010 can land first; SSE is the last bolt-on.
- **Soft:** FEAT-0004's backlinks panel will share the index from TASK-0007. Either feature can land first; whichever does, the other consumes the same module.

## Open questions to pin during implementation
- **`status.containsAny(...)` semantics.** Existing notes use scalar `status:` strings, but `containsAny` reads list-ish. Default interpretation: scalar field → "value is in the given set"; list field → set intersection. Confirm during TASK-0008.
- **Column-size units.** `columnSize: { note.id: 92 }` is in pixels in Obsidian. Carry the same unit; ignore on small screens.
- **`rowHeight: medium`.** Map to a CSS class with a sensible default; full Obsidian fidelity not required.
- **Group header sort direction when `groupBy.direction: ASC` collides with a `sort` rule.** Group-by direction wins for group order; sort applies within each group.
