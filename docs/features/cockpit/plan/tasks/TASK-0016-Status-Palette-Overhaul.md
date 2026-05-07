---
type: "[[task]]"
id: TASK-0016
aliases: ["TASK-0016"]
title: "Status palette overhaul (6 buckets) + Hide-completed expansion"
status: done
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-08
updated: 2026-05-08
source: ["[[CHG-20260508-Cockpit-Left-Modes-And-Palette]]"]
implements: ["[[FEAT-0006]]", "[[REQ-0012]]"]
fixes: []
effort: S
due: ""
depends: []
blocks: []
related: ["[[REQ-0012]]", "[[ADR-0003]]"]
tests: []
---

# TASK-0016 — Status palette overhaul

## Definition of Done
- [x] `base.css` defines exactly 6 status buckets per the [[REQ-0012]] table: `--status-active`, `--status-pending`, `--status-done`, `--status-archived`, `--status-blocked`, `--status-reference` (plus `--status-default` fallback). All values ≤60% saturation.
- [x] Both light and dark theme tokens defined; chip rules use `var(--token)` exclusively (no hard-coded hex/rgb in component CSS).
- [x] All real-world status values observed in this repo and `../your-trainer` map to a bucket: `active, approved, accepted, ready, doing, in-progress, in-review, next, planned, backlog, todo, open, pending, draft, proposed, triage, done, merged, fixed, fulfilled, met, complete, verified, passing, published, closed, obsolete, retired, cancelled, superseded, wont-fix, reverted, blocked, failing, reopened, reference, deferred`. Anything else falls through to `--status-default`.
- [x] `cockpit.css` stale references to dropped tokens (`--status-doing`, `--status-verified`, `--status-backlog`, `--status-triage`, `--status-closed`) updated to point at the new tokens. Priority chips re-mapped: high→blocked, medium→active, low→pending.
- [x] **Hide completed** in `cockpit.js` expanded to match both Done buckets — covers `done, merged, fixed, fulfilled, met, complete, verified, passing, published, closed, obsolete, retired, cancelled, superseded, wont-fix, reverted`. Previously only covered the v1 set (~9 values).

## Steps
- [x] Audit status vocabulary across both corpora (`grep -h "^status:"`); compare to the existing chip mapping.
- [x] Iterate the bucket table with the user (started at 11 buckets, settled on 6).
- [x] Edit `src/docs_server/static/base.css` — replace token block + replace per-status chip rules.
- [x] Update `src/docs_server/static/cockpit.css` priority-chip rules.
- [x] Update `COMPLETED_STATUSES` in `src/docs_server/static/cockpit.js`.

## Notes
- Closed (terminal-with-success) joins Done-positive per user direction; "off your radar" was deemed the right axis for the merge.
- Done-negative is desaturated grey rather than a colour, to stay quieter than Blocked's red while clearly marking "archived without success."
- In-review moved out of Triage and into Active (PR-up = in flight, not a sorting state).

Closed by: [[CHG-20260508-Cockpit-Left-Modes-And-Palette]].
