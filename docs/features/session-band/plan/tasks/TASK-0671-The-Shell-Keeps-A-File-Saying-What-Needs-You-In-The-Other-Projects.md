---
type: "[[task]]"
id: TASK-0671
aliases: ["TASK-0671"]
title: "The shell keeps a small file in each project's instrument folder saying what needs the person in every other project, counted by the same code as the home window"
status: backlog
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[FEAT-0157-The-Project-State-Sits-Above-The-Claude-Prompt]]", "plan/PLAN.md, 'needs-elsewhere.json in the instrument folder'"]
parent: "[[FEAT-0157-The-Project-State-Sits-Above-The-Claude-Prompt]]"
effort: "M"
due: ""
depends: []
blocks: ["[[TASK-0673-The-Cockpits-Facts-Join-The-End-Of-The-Project-Line]]", "[[TASK-0675-Cockpit-Needs-And-Cockpit-Release-Answer-In-A-Pane-Without-A-Turn]]"]
related: ["[[FEAT-0160-A-Draft-Window-Shows-What-Needs-You]]", "[[RISK-0004-Hook-Injection-Surface]]"]
tests: []
---

# The shell keeps a file saying what needs you in the other projects

A sidecar knows only its own project, so nothing a Claude session can reach knows what waits in the other projects. The shell does: the draft home window already counts every project. After this task the shell writes those counts into each project's instrument folder, beside `hook-env`, every 30 seconds. The cockpit plugin reads it for the line and for `/cockpit-needs`.

## Definition of Done

- [ ] The counting in `desktop/src/ipc/home-window.ts` (`buildProject`'s live obligations read and its cold `fleetHealth()` fallback) moves into one exported function. The home window calls it, and its existing tests pass unchanged.
- [ ] A new module in `desktop/src/ipc/` writes `needs-elsewhere.json` to every workspace's instrument folder in the shape plan/PLAN.md gives: `schema_version`, `written_at`, `workspace_id`, and `projects` listing every other workspace with `count`, `as_of` and `source` (`live`, `cold` or `unknown`). It never lists the folder's own workspace.
- [ ] Written every 30 seconds while the app runs, and at once when a workspace opens or closes; through a temporary file and a rename. Not written when `COCKPIT_NO_INSTRUMENT` is set. A failed write is logged and the previous file stays.
- [ ] A count that could not be read is `null` with `source: "unknown"`, never 0.
- [ ] Node tests that fail when: the own workspace appears in `projects`; an unread count is written as 0; the write is not atomic; the home window's number and the file's number for the same project differ.
- [ ] Capability register row `shell.fleet.needs-elsewhere` in the same commit as the change note that adds it.

## Steps

- [ ] Extract the counting function; keep the window's tests green.
- [ ] The writer, its timer and its hooks into workspace open and close.
- [ ] Tests and register row.

## Notes

The 30-second interval costs one obligations GET per live sidecar per tick. The home window already makes the same reads when open; the writer can share one result per tick with it if the window is open.
