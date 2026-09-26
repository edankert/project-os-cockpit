---
type: "[[change]]"
id: CHG-20260719-Live-Work-Views
aliases: ["CHG-20260719-Live-Work-Views"]
title: "Live work views — status-diff layer, session work tab, Active nav mode, phase-less Now board"
status: merged
owner: user:edwin
created: 2026-07-19
updated: 2026-07-19
source: []
commit: ""
pr: ""
reviewed_by: "model:claude-opus"
review_date: 2026-07-19
review_verdict: approved
impacts: ["new cockpit:status-change SSE + /api/cockpit/transitions", "new Active nav mode (server + renderer)", "session strip work tab", "phase-less overview Now board", "session work_notes field"]
issues: []
features: ["[[FEAT-0036-Live-Work-Views]]"]
related: ["[[TST-0018]]", "[[TASK-0162]]", "[[TASK-0163]]", "[[TASK-0164]]", "[[TASK-0165]]"]
---

# Live work views (FEAT-0036)

## Summary

**TASK-0162 — status-diff layer.** New `status_diff.py` (`StatusTracker`) subscribes to the docs watcher, parses each saved note's frontmatter, and — only on a real `status` change — publishes a `cockpit:status-change` control event (`{id, rel, type, title, from, to, ts}`) and logs it, served at `GET /api/cockpit/transitions`. Seeded from the index so a cold scan and first-appearances are silent. Guarded by TST-0018.

**TASK-0164 — Active nav mode.** New `active` mode (server `_active_groups`): in-flight items across all types, grouped Doing / Next / Done-today, newest activity first. The renderer live-migrates rows on `cockpit:status-change` (reload + flash) and shows an "agent" chip on rows a live session is touching.

**TASK-0163 — session work tab.** The agent-strip detail gains a work | files tab split; the work tab shows a status box per docs note the session touched (new broader `work_notes` field on the tracker — all note types, distinct from the narrow undocumented-work `docs_notes`), filled live as items go done.

**TASK-0165 — phase-less Now board.** A project with no `docs/phases/` gets a full-width Doing/Next/Done-today board on the overview centre instead of an empty phase grid, live-migrating on transitions.

## Verification

`tests/test_status_diff.py` (4) + full Python suite 216 passed / 1 skipped. CDP end-to-end: Active mode groups render; a session touching FEAT-0034 shows the agent chip on its Active row and a box in the work tab; a scratch note's triage→doing change live-migrates its row. `tsc` clean.

Independent review (opus) caught a dead work-tab click (rows searched the narrow docs_notes instead of the broad work_notes) and that the strip work-tab click now resolves via work_notes; both fixed. 

Files: `src/project_os_cockpit/{status_diff.py,server.py,cockpit.py,index.py,agent_hooks.py}`, `desktop/src/renderer/{index.html,renderer.ts,renderer.css}`, `tests/test_status_diff.py`.
