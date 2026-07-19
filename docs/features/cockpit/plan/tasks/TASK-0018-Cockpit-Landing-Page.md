---
type: "[[task]]"
id: TASK-0018
aliases: ["TASK-0018"]
title: "Cockpit landing page (root URL = cockpit shell, SNAPSHOT-driven home)"
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
depends: ["[[TASK-0013]]"]
blocks: []
related: ["[[REQ-0015]]"]
tests: ["[[TST-0002]]"]
---

# TASK-0018 — Cockpit landing page

## Definition of Done
- [x] `GET /` returns the cockpit HTML shell with `cockpit_active = null`, the JS client mounts left/right panes and header controls correctly with no active note.
- [x] Centre pane on `/` renders synthetic home from `SNAPSHOT.yaml`: project header, focus block, phase progress, at-a-glance counts, recent changes (top 5).
- [x] Falls back to `docs/README.md` when SNAPSHOT.yaml is missing or unparseable.
- [x] Falls back to a minimal landing summary when neither exists (no 500).
- [x] Right pane shows an empty-state ("Select a note to see relationships") when active note is null.
- [x] Acceptance tested against this repo's `docs/` (snapshot present) and against a synthetic temp dir with no snapshot (README fallback exercised).

## Steps
- [x] Add `home_page_html()` builder in `src/docs_server/templates.py` taking the parsed SNAPSHOT, the index, and the docs root name.
- [x] Snapshot loader helper: `_load_snapshot(repo_root)` returning a dict or `None`.
- [x] Update `_serve_landing` in `src/docs_server/server.py` to render the cockpit shell with the synthetic home as the centre body.
- [x] CSS for the home layout (focus cards, phase rows, counts grid, recent list) in `cockpit.css`.
- [x] Empty-state placeholder in cockpit.js for when `cockpit-config.active` is null.
