---
type: "[[feature]]"
id: FEAT-0161
aliases: ["FEAT-0161"]
title: "The Tests page shows a test run as it happens, each command linked to its log, and the latest CI run of each workflow"
status: doing
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
owner: user:edwin
created: 2026-10-22
updated: 2026-10-22
source:
  - "[[project-os-dev#FEAT-0042-Test-Runs-And-CI-Results-Can-Be-Seen]], Edwin 2026-10-22: 'Plan and build, in one go, a way to see test progress while tests run, and to see CI failures, for every project-os project'"
  - "project-os-dev TASK-0216, the cockpit's part of that feature"
goal: "A person on the cockpit's Tests page sees how far the repo's latest test run has got while it runs, one block per command, with the failing, timed-out and running commands listed and each one linked to its log. Below it they see the latest CI run of each workflow, with its failing tests and a link to the run. Both fill in without a reload."
requirements: []
tasks:
  - "[[TASK-0681-The-Tests-Page-Reads-The-Run-And-CI-Files-Watches-Them-And-Serves-The-Logs]]"
release: ""
acceptance_exception: ""
acceptance: ""
design: ""
reviewed_by: ""
review_date: ""
review_verdict: ""
review_round: ""
related:
  - "[[FEAT-0086-Tests-Becomes-A-View]]"
  - "[[FEAT-0128-The-Tests-View-Leads-With-The-Work]]"
  - "[[FEAT-0092-Every-View-Lands-On-What-It-Owes]]"
---

# The Tests page shows the live test run and the latest CI run

## Goal

A person on the cockpit's Tests page sees how far the repo's latest test run has got while it runs, and which commands have failed so far. Each command is one coloured block, and each failing, timed-out or running command also gets a row with its test IDs, how long it took and why. Under that, each CI workflow's latest run says whether it passed, failed or is still running, names its failing tests, and links to the run on GitHub. Both parts redraw when their file changes, without reloading the page.

## Why

In your-trainer on 2026-10-21, a `git push` sat in the pre-push hook for hours while `run-tests.py` ran 139 commands, and nothing showed how far it had got. TST-0022 failed in the first minutes and nobody knew for over an hour. project-os-dev FEAT-0042 makes `run-tests.py` write a progress file and adds `ci-status.py`, which saves CI's latest runs to a second file. This feature is the cockpit's reader of both files.

## Scope

In:

- A "Latest test run" section at the top of the Tests page (`~tests`), read from `<repo>/.project-os/runs/latest.json`: a header line, one block per command in run order, and a row for each failing, timed-out, unrunnable, running or interrupted command.
- The symbols the terminal view (`test-status.py`) uses, so the two read alike: passing ■, failing ✗, timed out ⧗, unrunnable ?, running ▶, waiting □, interrupted ‖.
- A run file that says `running`, written on this machine by a runner whose process is gone, is shown as stopped.
- Each block and row opens that command's log, served by the sidecar. The sidecar serves only a log the run file names, under `.project-os/runs/`.
- A "CI" section read from `<repo>/.project-os/ci/latest.json`: per workflow, the latest run's state, commit, how long ago, failing tests or failing jobs, and a link to the run. The file's `error`, when set, in one line.
- A watcher on `.project-os/runs/` and `.project-os/ci/` that publishes `cockpit:test-run` on the sidecar's live events, so the page re-fetches and redraws both sections.
- With no run file or no CI file, one line each says so. A file in an unknown format version is shown as unreadable.

Out:

- Writing either file. `run-tests.py` and `ci-status.py` in the project-os template do that (project-os-dev FEAT-0042).
- Showing earlier runs. Only `latest.json` is read.
- The sidecar's own browser page (`static/cockpit.js`), which has no Tests page.

The formats are defined once, upstream, in `tools/instructions/TEST-RUNS.md` of the project-os template.

## Acceptance

- With `.project-os/runs/latest.json` present, the Tests page shows a header naming the repo, the run's source, its elapsed time and how many commands have finished, then one block per command in the file's order, each in its state's colour and symbol.
- Under the blocks, each failing, timed-out, unrunnable, running or interrupted command has a row with its test IDs, its state, how long it took, its reason, and for a running command its progress line, such as `12/60 AddRiderFlowTest`.
- A run whose state is `running`, whose `host` is this machine and whose `pid` is not alive reads as stopped, and its running command as interrupted.
- Clicking a block or a row opens that command's log. `GET /api/cockpit/test-run/log` refuses any path the run file does not name, and any path that resolves outside `.project-os/runs/`.
- The CI section shows each workflow's latest run as passing, failed or running, with a 7-character commit, how long ago, its failing test IDs or failing jobs, and a link to the run. A set `error` shows in one line.
- When either file is rewritten, the sidecar publishes `cockpit:test-run` and the open Tests page redraws both sections without a reload.
- With no run file, the section reads "No test run yet. `python3 tools/scripts/run-tests.py` writes one." With no CI file, the CI section says so in one line. The rest of the Tests page is unchanged.
- A file with an unknown `version`, a different `format`, or JSON that does not parse is shown as unreadable, in one line, and nothing else on the page breaks.

## Verification

Filled at close-out.

## Links

- Task: [[TASK-0681-The-Tests-Page-Reads-The-Run-And-CI-Files-Watches-Them-And-Serves-The-Logs]]
- Plan: `plan/PLAN.md`
- Upstream: [[project-os-dev#FEAT-0042-Test-Runs-And-CI-Results-Can-Be-Seen]], project-os-dev TASK-0216
- Code: `src/project_os_cockpit/test_runs.py`, `src/project_os_cockpit/server.py`, `desktop/src/renderer/test-run.ts`, `desktop/src/renderer/renderer.ts`
