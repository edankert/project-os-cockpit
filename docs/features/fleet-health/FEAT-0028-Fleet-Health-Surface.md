---
type: "[[feature]]"
id: FEAT-0028
aliases: ["FEAT-0028"]
title: "Fleet health surface — per-workspace validator badges across all discovered repos"
status: done
phase: "[[PHASE-013-Fleet-Surfaces]]"
owner: user:edwin
created: 2026-07-17
updated: 2026-07-17
source: []
goal: "The desktop shell shows a per-workspace docs-validation badge for every SNAPSHOT-bearing repo it knows about, so drift anywhere in the fleet is visible from one place without opening each project."
requirements: []
tasks: ["[[TASK-0248-Live-Workspace-Validation-Aggregate]]", "[[TASK-0249-Cold-Workspace-Validation]]", "[[TASK-0250-Fleet-Badge-On-The-Rail]]", "[[TASK-0251-Fleet-Roll-Up]]"]
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


## Breakdown — 2026-07-30

Four tasks, sequenced so the cheap half ships without waiting on the expensive one: [[TASK-0248]] (live workspaces, pure reuse of FEAT-0018's endpoint and SSE), [[TASK-0249]] (cold workspaces, and the decision below), [[TASK-0250]] (the badge), [[TASK-0251]] (the roll-up). Plan in `plan/PLAN.md`.

**This feature's brief plan contradicts an existing script, and the breakdown does not paper over it.** Step 2 above says *"run the repo's `tools/scripts/validate-docs.py`"*; `tools/scripts/validate-fleet.sh` says *"uses THIS repo's validate-docs.py for uniform semantics"*. Those produce different badges for the same repo — per-repo honours a pinned older template, uniform makes counts comparable. [[TASK-0249]] owns the decision and must record it before implementing.

**Step 3's "following the agent-state dot pattern" understates a collision.** The rail entry already *has* a `.ws-dot`, and it is agent state. A validator dot there is two signals on one channel in a smaller space than [[DES-0004]] dealt with. [[TASK-0250]] carries three options and a recommendation to render them rather than argue them.

**No `TST-*` note yet, deliberately.** The convention here is to author one at planning time, but a `ready` test now carries an attention dot on the phase strip ([[DES-0004]]), and a dot for work nobody has started would be a false signal on a surface built to remove them. The tests are specified in each task's Steps; the note comes with the first implementation. That tension is worth watching — it is the encoding making a documentation habit visible, which is a small argument that the habit was carrying an unstated assumption.


## Done 2026-07-30

All four tasks landed and were verified against the real fleet — ten discovered workspaces, one deliberately drifted. Evidence in [[TASK-0250]]'s and [[TASK-0251]]'s live-pass sections.

The three acceptance criteria:

1. **Two workspaces, one drifting** — met, and stronger than asked: ten repos, one drifting, badge `1` on that square alone, cleared over SSE without restarting the shell. Both signals coexisted on the same square (`state-busy health-failing`).
2. **A discovered-but-not-running workspace still gets a state** — met. All ten validated cold on startup, `source: 'cold'`, and rows age into `stale` past their schedule.
3. **Zero new Python dependencies; validator logic stays in `validate-docs.py`** — met. `fleet_validate.py` is stdlib and delegates to `ValidationRunner`, which shells out to the validator.

### The two contradictions the breakdown surfaced, both resolved

- **Whose validator runs** → the repo's own, matching `ValidationRunner`'s locate order and its stated reason. `validate-fleet.sh` keeps the uniform choice, which is right for a manual diagnostic and wrong for a badge. Recorded in [[TASK-0249]] before implementing, pinned by a test.
- **The rail-dot collision** → resolved on semantics rather than taste: different corner, different shape, and a *numeral* rather than a fill. See [[TASK-0250]].

### Owed

- **[[ISS-0072]]**, found during the live pass: the sidecar's `SNAPSHOT.yaml` observer never fires, so `METRICS` drift — the commonest validator error — cannot clear live. [[FEAT-0018]]'s machinery, not this feature's, and this feature's path is unaffected.
- The DoD's "and tabs" describes a surface this shell does not have; it has a workspace rail. Said rather than ticked.
- The roll-up has no automated test — DOM code in `renderer.ts` cannot be imported outside a browser. Covered by the live pass, marked `[~]`.
