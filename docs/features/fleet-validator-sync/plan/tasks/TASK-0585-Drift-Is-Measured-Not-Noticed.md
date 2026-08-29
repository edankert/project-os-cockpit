---
type: "[[task]]"
id: TASK-0585
aliases: ["TASK-0585"]
title: "Drift is measured, not noticed — a check that reports every fleet validator's divergence from upstream and fails past a stated threshold"
status: done
phase: "[[PHASE-041-The-Gate-Runs-Where-The-Checks-Are]]"
owner: user:edwin
created: 2026-08-29
updated: 2026-08-29
source: ["[[ISS-0209-The-Acceptance-Gate-Reaches-No-Fleet-Repo]]"]
parent: "FEAT-0143"
effort: ""
due: ""
depends: ["TASK-0581"]
blocks: []
related: []
tests: ["[[TST-0081]]"]
---

# Drift is measured, not noticed

## Definition of Done
- [x] `tools/scripts/fleet-drift.py` reports each `SNAPSHOT.yaml`-bearing repo's `validate-docs.py` divergence from upstream, and its acceptance-gate presence.
- [x] It **fails** past a stated threshold, and the threshold is written down with its reason rather than chosen.
- [x] A repo with no validator, and a missing upstream, are distinguishable outcomes — not both "0".
- [x] Guarded by [[TST-0081]], which exercises the failing branch rather than asserting the passing one.

## Notes

This is in [[PHASE-041]]'s goal rather than a follow-up for a measured reason: divergence grew **~93 lines in eleven days, uniformly across all four repos**, while nobody did anything wrong. A one-shot catch-up regresses on a schedule.

The check reports on repos this app can see but does not own. It is **read-only** and reports; it never edits a fleet repo. `fleet_validate` and `fleet_git` set that precedent.
