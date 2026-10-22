---
type: "[[plan]]"
title: "Delivery plan: the live test run and CI on the Tests page"
status: active
owner: user:edwin
created: 2026-10-22
updated: 2026-10-22
source: ["[[FEAT-0161-The-Tests-Page-Shows-The-Live-Test-Run-And-The-Latest-CI-Run]]"]
implements: ["[[FEAT-0161-The-Tests-Page-Shows-The-Live-Test-Run-And-The-Latest-CI-Run]]"]
related: ["[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]", "[[project-os-dev#FEAT-0042-Test-Runs-And-CI-Results-Can-Be-Seen]]"]
---

<!-- Plans deliberately carry no `id:` / `aliases:`; see docs/__templates__/plan.md. -->
# Delivery plan: the live test run and CI on the Tests page

The feature is one task, [[TASK-0681-The-Tests-Page-Reads-The-Run-And-CI-Files-Watches-Them-And-Serves-The-Logs]], built in this order.

## Delivery sequence

1. **Reading the two files.** A new module, `src/project_os_cockpit/test_runs.py`, reads `.project-os/runs/latest.json` and `.project-os/ci/latest.json` and turns each into what the page draws: header text, each command's symbol and duration, the rows to list, and each workflow's state. The page then works nothing out itself, the way the release test page takes its sections from the payload. A missing file, a file that does not parse, a different `format` and an unknown `version` each become a one-line answer instead of an error.
2. **The routes.** `GET /api/cockpit/test-run` returns both readings. `GET /api/cockpit/test-run/log?path=` returns one command's log as plain text, only for a path the run file names that resolves under `.project-os/runs/`. Both are loopback-only, like the inbox's read routes, because a log can hold whatever a test printed.
3. **The watcher.** `.project-os/` sits beside `docs/`, outside the main watcher, as `SNAPSHOT.yaml` does. A small observer in `test_runs.py` watches `runs/` and `ci/` without recursing (the logs inside `runs/<id>/` change on every line), and publishes `cockpit:test-run` when either `latest.json` is created, replaced or changed. The folders may not exist when the sidecar starts, so the watcher checks every few seconds for one that has appeared.
4. **The page.** A new renderer file, `desktop/src/renderer/test-run.ts`, loaded as a plain script like `release-test.ts`, draws the two sections. `renderViewLanding('tests')` places them under the Tests heading. The `cockpit:test-run` event repaints only those sections. While a run reads as running, the page also re-fetches every 15 seconds, so the elapsed time moves and a runner that died without writing is seen as stopped.
5. **Tests, register and change note.** Pytest cases for the readings, the routes, the log refusal, the stopped runner and the watcher's event. The capability register gains its rows in the change note's commit.

## What the implementation must not do

- Write to `.project-os/` or create it.
- Serve any file the run file does not name, or any path outside `.project-os/runs/`.
- Treat either file as a verdict. A test note's status is unchanged by anything shown here (project-os ADR-0025).
- Change how the rest of the Tests page is drawn.
