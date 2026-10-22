---
type: "[[task]]"
id: TASK-0681
aliases: ["TASK-0681"]
title: "The Tests page reads the run and CI files, redraws when they change, and opens each command's log"
status: done
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
owner: user:edwin
created: 2026-10-22
updated: 2026-10-22
source: ["[[FEAT-0161-The-Tests-Page-Shows-The-Live-Test-Run-And-The-Latest-CI-Run]]", "project-os-dev TASK-0216"]
parent: "[[FEAT-0161-The-Tests-Page-Shows-The-Live-Test-Run-And-The-Latest-CI-Run]]"
effort: "M"
due: ""
depends: []
blocks: []
related: []
tests: []
---

# The Tests page reads the run and CI files, redraws when they change, and opens each command's log

## Definition of Done
- [x] `test_runs.py` reads both files, including a missing file, one that does not parse, a different `format`, an unknown `version`, and a file missing optional keys.
- [x] A `running` run from this machine whose runner is gone reads as stopped.
- [x] `GET /api/cockpit/test-run` returns both readings; `GET /api/cockpit/test-run/log` serves a named log and refuses anything else.
- [x] Rewriting either `latest.json` publishes `cockpit:test-run`.
- [x] The Tests page draws both sections at the top and redraws them on the event.
- [x] Pytest cases cover each of the above; the full suite passes.
- [x] Change note and capability register rows.

## Steps
- [x] `src/project_os_cockpit/test_runs.py`: readers, log check, watcher
- [x] `server.py`: two routes, watcher start and stop
- [x] `desktop/src/renderer/test-run.ts`, `renderer.ts`, `renderer.css`, `index.html`
- [x] `tests/test_test_runs.py`
- [x] Change note, register, close-out

## Notes

Done 2026-10-22 in commit 98ffb90, with the change note [[CHG-20261022-The-Tests-Page-Shows-The-Live-Test-Run-And-The-Latest-CI-Run]]. `tests/test_test_runs.py` has 27 cases; the full suite's one failure is the stale `desktop/dist/` build, which `npm run build` in `desktop/` clears (see the change note's Verification).

This is the cockpit's part of [[project-os-dev#FEAT-0042-Test-Runs-And-CI-Results-Can-Be-Seen]], project-os-dev TASK-0216. The two file formats are defined in the project-os template's `tools/instructions/TEST-RUNS.md` (project-os-dev FEAT-0042), and were read on 2026-10-22, while project-os-dev was writing `run-tests.py` and `ci-status.py` beside this task. This task only reads the files.
