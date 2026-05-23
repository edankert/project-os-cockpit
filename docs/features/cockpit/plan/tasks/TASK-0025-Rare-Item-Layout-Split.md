---
type: "[[task]]"
id: TASK-0025
aliases: ["TASK-0025"]
title: "Cockpit: split rare-item shapes (typed-rare keep id+title; references show filename in id slot); right-align status chip"
status: done
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-09
updated: 2026-05-23
source: []
implements: ["[[FEAT-0006]]", "[[REQ-0012]]", "[[REQ-0016]]"]
fixes: []
effort: S
due: ""
depends: ["[[TASK-0022]]", "[[TASK-0023]]"]
blocks: ["[[TASK-0026]]"]
related: ["[[TASK-0022]]"]
tests: ["[[TST-0002]]"]
---

# TASK-0025 — Split rare-item shapes; right-align status chip

## Definition of Done
- [x] Typed-structured rare types (decisions, releases, risks, tests, workflows, plans) revert to the original `id + human title` shape — the filename + path subtitle introduced in TASK-0022 is removed for these.
- [x] References show the **filename** in the `id` slot (mono); the human frontmatter title still renders below, suppressed when it duplicates the filename stem.
- [x] Pinned section keeps the typed-structured shape (id + human title).
- [x] Status chip is right-aligned in `navItem`, `navItemStacked`, and `ctxItem` so the type icon owns the left edge.
- [x] Tests pass; new test asserts both the typed-rare shape (against a synthetic ADR fixture) and the references shape.

## Steps
- [x] Restored original `_rare_item` (id + title); added `_reference_item` (filename in id slot).
- [x] Routed `type_name == "reference"` through `_reference_item` in `_library_groups`; everything else through `_rare_item`.
- [x] Restructured top lines in `cockpit.js` (`navItem`, `navItemStacked`, `ctxItem`) — status is now the last child; spacer span where there's no flex-grow item.
- [x] Added `.nav-line-spacer { flex: 1 1 auto; }` and removed `margin-left: auto` from `.ctx-priority` (the spacer handles right-alignment now).
- [x] Removed `mono` from `.nav-title-stacked` so typed-rare titles render in the regular weight (not monospace).
- [x] Tests rewritten: removed the all-rare-types filename assertion; added typed-rare and reference-only assertions.

## Notes
The earlier "filename + parent dir" treatment from TASK-0022 was over-applied — typed rare notes have meaningful titles and live in conventional dirs, so the filename and path subtitle were noise. Only References — loose docs with no real ID — benefit from filename-in-id-slot.
