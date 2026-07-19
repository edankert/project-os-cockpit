---
type: "[[feature]]"
id: FEAT-0028
aliases: ["FEAT-0028"]
title: "Fleet health surface — per-workspace validator badges across all discovered repos"
status: backlog
phase: "[[PHASE-999-Future]]"
owner: user:edwin
created: 2026-07-17
updated: 2026-07-17
source: []
goal: "The desktop shell shows a per-workspace docs-validation badge for every SNAPSHOT-bearing repo it knows about, so drift anywhere in the fleet is visible from one place without opening each project."
requirements: []
tasks: []
release: ""
related: ["[[FEAT-0018-Verification-Health-Surface]]", "[[FEAT-0007-Desktop-Shell]]"]
tests: []
---

# Fleet health surface

## Goal
FEAT-0018 makes verification drift visible for the repo currently being browsed. This feature aggregates that signal across the whole fleet: every workspace the desktop shell has discovered (each with a `SNAPSHOT.yaml`) surfaces its validator state — green / red-with-count / grey — on its workspace tab / mini-rail entry, plus a roll-up view answering "is anything drifting anywhere?" at a glance. This was explicitly out of scope for FEAT-0018 ("running the validator against repos not currently being browsed"); the desktop shell is the natural home for it.

## Brief plan
1. **Per-sidecar signal (no new machinery):** each running workspace sidecar already exposes `GET /api/cockpit/validation` and the `cockpit:validation` SSE event (TASK-0111). The shell's main process consumes those for live workspaces.
2. **Cold workspaces:** for discovered repos without a running sidecar, run the repo's `tools/scripts/validate-docs.py` (bundled fallback, same locate rules as `ValidationRunner`) on a slow poll / on-focus schedule from the main process, reusing the parsed-report shape.
3. **Rail/tab badges:** render the tri-state dot on workspace tabs and the mini-rail, following the agent-state dot pattern (TASK-0082); tooltip carries error count + last-checked time.
4. **Fleet roll-up:** a small aggregate surface (menu popover or overview block) listing drifting workspaces with error counts, deep-linking into the workspace's drift panel (TASK-0112).

## Scope
- In: desktop shell (mode 3) only; read-only surfacing; per-workspace tri-state + counts; roll-up list.
- Out: auto-fixing drift; running validators for repos never added as workspaces; mode-1 browser (single-repo by design).

## Acceptance
- With two workspaces open and one drifting, the drifting workspace's tab/rail entry shows a red badge with the error count while the other stays green; fixing the drift clears the badge without restarting the shell.
- A discovered-but-not-running workspace still gets a (possibly stale-marked) validation state.
- Zero new Python dependencies; validator logic stays in `validate-docs.py`.

## Links
- Builds on: [[FEAT-0018-Verification-Health-Surface]] (endpoint + SSE), [[FEAT-0007-Desktop-Shell]] (workspace discovery), TASK-0082 (rail dots pattern).
