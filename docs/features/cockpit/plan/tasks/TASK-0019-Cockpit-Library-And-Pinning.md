---
type: "[[task]]"
id: TASK-0019
aliases: ["TASK-0019"]
title: "Cockpit Library mode + pin button"
status: done
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-08
updated: 2026-05-08
source: []
parent: "[[FEAT-0006]]"
fixes: []
effort: M
due: ""
depends: ["[[TASK-0015]]"]
blocks: []
related: ["[[REQ-0016]]"]
tests: ["[[TST-0002]]"]
---

# TASK-0019 — Cockpit Library mode + pinning

## Definition of Done
- [x] `nav_payload(index, mode="library", pinned=[...])` returns three sections: Pinned (resolved from query), Project handles (auto-discovered), By type — rare (collapsible per type).
- [x] Project-handles discovery: docs-root *.md without ID prefix + canonical-subdir *.md without ID prefix (excluding `README.md` files inside subdirs).
- [x] By-type-rare groups render only when at least one note of that type exists.
- [x] `?pinned=path1,path2` query param parsed into the call; missing/empty means no pinned section.
- [x] JS adds Library to `NAV_MODES`; renders pinned section using the server-resolved data.
- [x] Pin button in header (star icon, next to theme toggle) — toggles the active note's path in `localStorage` (`docs-server.cockpit.pinned-paths`). Filled when pinned.
- [x] Pin button is omitted when there's no active note (the synthetic landing).
- [x] Pinning a note while Library mode is visible re-renders the pane immediately.
- [x] Stale pinned paths (file deleted) are silently dropped server-side; localStorage is pruned on the next response.
- [x] Tests for project-handle discovery, by-type-rare grouping, pin resolution, stale-pin pruning.

## Steps
- [x] Add `_library_groups(index, pinned)` to `src/docs_server/cockpit.py`. Use a regex for the ID-prefix exclusion. Walk `docs/` for top level + canonical subdirs.
- [x] Register `library` in `NAV_MODES`.
- [x] Update server query parsing to forward `pinned` to `nav_payload`.
- [x] JS: extend `NAV_MODES`, persist+resolve pinned paths, render pinned/handles/rare sections.
- [x] JS: add pin button to the page header. Read active note's path from `cockpit-config`. Toggle via localStorage.
- [x] CSS: pin button (star glyph, hover + active states), Library section dividers.
- [x] Tests: extend fixture with a top-level `README.md` (handle), a `tests/ACCEPTANCE_TESTS.md` (curated subdir), and at least one ADR/release/risk so the rare-types groups have content.
