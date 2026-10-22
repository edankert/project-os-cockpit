---
type: "[[change]]"
id: CHG-20261022-The-Tests-Page-Shows-The-Live-Test-Run-And-The-Latest-CI-Run
title: "The Tests page shows the repo's latest test run as it happens, each command linked to its log, and the latest CI run of each workflow"
status: merged
owner: user:edwin
created: 2026-10-22
updated: 2026-10-22
source: ["[[TASK-0681-The-Tests-Page-Reads-The-Run-And-CI-Files-Watches-Them-And-Serves-The-Logs]]"]
commit: "98ffb90"
pr: ""
impacts: ["src/project_os_cockpit/test_runs.py", "src/project_os_cockpit/server.py", "desktop/src/renderer/test-run.ts", "desktop/src/renderer/renderer.ts", "desktop/src/renderer/renderer.css", "desktop/src/renderer/index.html", "tests/test_test_runs.py", "tests/test_remote_peer_refusal.py"]
platforms: []
issues: []
features: ["[[FEAT-0161-The-Tests-Page-Shows-The-Live-Test-Run-And-The-Latest-CI-Run]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: []
---

# The Tests page shows the live test run and the latest CI run

## Summary

The Tests page now opens with the repo's latest test run and its latest CI runs. While `run-tests.py` runs, for example in a pre-push hook, a person can see how many commands have finished, which have failed so far, and what the running one is doing, and open any command's log. Under that, each CI workflow says whether its latest run passed, failed or is still running, names its failing tests, and links to the run on GitHub. Both parts redraw when their file changes, without a reload.

This is the cockpit's part of [[project-os-dev#FEAT-0042-Test-Runs-And-CI-Results-Can-Be-Seen]] (project-os-dev TASK-0216). project-os's `run-tests.py` and `ci-status.py` write the two files; the template's `tools/instructions/TEST-RUNS.md` defines their formats.

## What changed

- **Latest test run.** Read from `.project-os/runs/latest.json`. A header line such as `your-trainer · pre-push · 1h10m · 44 of 139 commands`, then one block per command in run order, in the terminal view's symbols: passing ■, failing ✗, timed out ⧗, unrunnable ?, running ▶, waiting □, interrupted ‖. Under the blocks, one row for each failing, timed-out, unrunnable, running or interrupted command, with its test IDs, state, duration and reason; a running command shows its progress line instead, such as `12/60 AddRiderFlowTest`.
- **A dead runner reads as stopped.** A run file that still says `running`, written on this Mac by a process that no longer exists, reads "stopped: runner 48213 is no longer running and the run never finished", and its running command reads as interrupted.
- **Logs.** Clicking a block or a row opens that command's log as plain text in the browser. The sidecar serves only a log the run file names and that resolves under `.project-os/runs/`; any other path gets a 404. A log over 4 MB is sent from its end, with a first line saying how much was left out.
- **CI.** Read from `.project-os/ci/latest.json`. One row per workflow: its latest run's state, a 7-character commit, how long ago, its failing test IDs or failing jobs, and an "open run" link. A workflow still running after a failed run also names that failure. The file's `error`, when set, shows in one line above the rows.
- **Missing or unreadable files.** With no run file the section reads "No test run yet. `python3 tools/scripts/run-tests.py` writes one."; with no CI file, "No CI result yet. `python3 tools/scripts/ci-status.py` fetches one." A file that does not parse, of another format, or of a format version this cockpit does not know reads as unreadable in one line. The rest of the Tests page is drawn as before.
- **Live.** The sidecar watches `.project-os/runs/` and `.project-os/ci/`, not their subfolders, and publishes `cockpit:test-run` with `{"what": ["run"]}` or `["ci"]` when either `latest.json` is replaced. A folder that appears after the sidecar started is picked up within three seconds. The page redraws only the two sections, and re-fetches every 15 seconds while a run is live.
- **Routes.** `GET /api/cockpit/test-run` returns both readings; `GET /api/cockpit/test-run/log?path=` returns one log. Both are loopback-only, because a log holds whatever a test printed.

## What a person notices

- During a push in your-trainer, the Tests page shows the grid filling in, and the failing TST-0022 row appears as soon as its command ends, with a link to its log.
- After a push, the CI section shows `android-tests · failed · 8bf1562 · 23m ago · TST-0022` until a later run passes.
- A repo that has never run `run-tests.py` shows two one-line sections and its usual Tests page.

## Verification

- `tests/test_test_runs.py`: 27 cases covering both readers (present, absent, not JSON, another format, unknown version, missing optional keys, an unknown command state), the stopped runner and the three cases that cannot be judged stopped, the log refusals (unnamed, outside `runs/`, absolute, a symlink out of `runs/`), both routes over a real socket including a refusal from a network peer, and the watcher through the real observer with no `.project-os/` at start. Removing the named-log check, the `runs/` containment, the dead-runner check, the format-version check or the watcher's announcement of a new folder each makes at least one case fail.
- A scratch sidecar on a fixture repo answered both routes, refused an unnamed log with 404, and sent `cockpit:test-run` on `/_events` for a CI file written into a new folder and for a rewritten run file. The panel was rendered from that sidecar's payload in headless Chrome and read as described above.
- Full Python suite, 2026-10-22: 2281 passed, 11 skipped, 1 failed. The failure is `test_desktop_build_is_not_stale`, which compares the built `desktop/dist/` with the TypeScript source and passes after `npm run build` in `desktop/`. The build was not run, because it rewrites the files of the desktop cockpit Edwin had running.
- `npx tsc --noEmit` in `desktop/` is clean.
