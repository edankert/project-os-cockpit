---
type: "[[change]]"
id: CHG-20260720-Progress-Counts-Terminal-Resolved
aliases: ["CHG-20260720-Progress-Counts-Terminal-Resolved"]
title: "Overview progress counts terminal-resolved items — retired requirements + superseded features complete the bar"
status: merged
owner: user:edwin
created: 2026-07-20
updated: 2026-07-20
source: []
commit: ""
pr: ""
reviewed_by: "model:claude-opus"
review_date: 2026-07-20
review_verdict: approved
impacts: ["scoped stats completion sets (DONE_FEAT / DONE_REQ / DONE_PHASE_BUCKET)"]
issues: []
features: ["[[FEAT-0023-Overview-Scopes]]"]
related: ["[[TASK-0176]]"]
---

# Overview progress counts terminal-resolved items

## Summary

The overview never reached 100% for a phase containing terminal-resolved items: the completion sets in `cockpit.py` omitted `retired` (requirements) and `superseded` (features), so a retired requirement or superseded feature was bucketed as backlog and counted against completion — e.g. PHASE-002 stuck at ~98% because of retired REQ-0009/0010/0011 and superseded FEAT-0004. Fix: `retired`, `superseded`, and `cancelled` are terminal, resolved outcomes and now count as done consistently across the hero tiles (`DONE_FEAT`/`DONE_TASK`/`DONE_REQ`) AND the phase bar/drill-down (`DONE_PHASE_BUCKET`). Previously `cancelled` counted only in the bucket, so a phase's hero task tile could read 45/47 while its bar showed 100% — that hero-vs-bar split was PHASE-002's actual shortfall (cancelled TASK-0042/0046). `deferred` (parked, still intended) is deliberately left as open work.

## Verification

Test `test_retired_and_superseded_count_as_done` (hero counts incl. a cancelled task + phase progress bucket + drill-down loose items) — passes with the fix, fails without. PHASE-002 hero now reports features 2/2, tasks 47/47, requirements 9/9 — all tiles agree with the bar at 100%. Full suite 221 passed. Independent review requested harmonising `cancelled` across hero and bucket (done).

Also repaired two frontmatter corruptions introduced by earlier edits this session that had silently excluded their files from the index: a stray C1 control character in the `CHG-20260720-Usage-Freshness` title (mojibake-cleanup residue) and a malformed `tasks:` YAML list in `FEAT-0007-Desktop-Shell` (a regex that matched the first `]` inside `[[TASK-0058]]`). Index now builds cleanly with no parse-failed warnings.

Files: `src/project_os_cockpit/cockpit.py`, `tests/test_stats_scope.py`, `docs/changes/CHG-20260720-Usage-Freshness.md`, `docs/features/desktop-shell/FEAT-0007-Desktop-Shell.md`.
