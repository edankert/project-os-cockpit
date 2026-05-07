---
type: "[[plan]]"
id: PLAN-FEAT-0006
title: "Plan: 3-pane cockpit layout (code-driven)"
status: active
owner: user:edwin
created: 2026-05-07
updated: 2026-05-08
implements: ["[[FEAT-0006]]"]
related: ["[[ADR-0004]]", "[[REQ-0013]]"]
---

# Plan — FEAT-0006 Cockpit Layout

## Delivery sequence
1. **[[TASK-0007]] — Note index + backlink graph.** *(done)*
   In-memory data layer: lookup tables, outbound/inbound graph, `invalidate(path)` hook for the watcher.
2. **[[TASK-0012]] — Cockpit JSON API.**
   `GET /api/cockpit/nav` (features-by-phase) and `GET /api/cockpit/context?this=<note>` (outbound + inbound-only). Pure data, no HTML. Schema-versioned (`X-Cockpit-Schema: 1`) so the JS client can detect bumps.
3. **[[TASK-0013]] — Cockpit shell + JS renderer.**
   3-pane HTML shell wrapping every note page; `cockpit.js` reads `#cockpit-config`, fetches both endpoints, renders the panes, intercepts in-pane navigation. CSS in `cockpit.css`, token-driven per [[REQ-0012]].
4. **[[TASK-0014]] — SSE-driven pane re-fetch.**
   `cockpit.js` subscribes to `/_events`. Feature-note edits trigger a left-pane re-fetch; active-note edits trigger a right-pane re-fetch; unrelated edits are ignored. 100 ms per-pane debounce.

## Dependencies
- **Hard:** TASK-0007 done (link graph data layer).
- **Hard:** FEAT-0001 done (renderer for the centre pane).
- **Hard:** FEAT-0002 done (SSE channel for TASK-0014).

All hard deps are met as of 2026-05-08.

## Open questions to pin during implementation
- **Centre-pane swap mechanic.** When clicking a feature in the left pane, the centre pane needs to update. Two options:
  1. `fetch` the new note's HTML, parse with `DOMParser`, swap `.content`. Theme + scroll + state preserved.
  2. Server-rendered cockpit always — full page reload on nav. Simpler but loses left-pane scroll.
  
  Recommend (1). Decided in TASK-0013.
- **Inbound-only visual distinction.** A muted text colour + an arrow glyph (`←` for inbound-only, `→` for outbound)? A separate section heading with subtitle? Land-time decision; not worth pre-committing.
- **What counts as a "feature edit" for left-pane re-fetch?** Any change to a `.md` whose path matches `features/<slug>/FEAT-####-*.md`, OR any change whose `type: feature`. Path heuristic is cheaper for the JS client. TASK-0014 picks one.

## Out of plan (deferred — see ADR-0004)
- `.base` parser + DSL evaluator ([[TASK-0008]])
- `.base` JSON API ([[TASK-0009]])
- Generic `.base`-mounted cockpit shell ([[TASK-0010]])
- Generic cockpit SSE re-fetch ([[TASK-0011]])
- "Bases as source of truth" / configurable mounts / `this.file` propagation requirements ([[REQ-0009]] / [[REQ-0010]] / [[REQ-0011]])

These remain in-tree at `status: backlog` (tasks) / `retired` (REQs) in case a future "`.base` rendering" feature appears. They are NOT prerequisites for any of TASK-0012/13/14.
