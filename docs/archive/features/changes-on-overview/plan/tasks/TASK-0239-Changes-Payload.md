---
type: "[[task]]"
id: TASK-0239
aliases: ["TASK-0239"]
title: "Changes payload — recent plus the existing buckets, at /api/cockpit/changes"
status: done
phase: "[[PHASE-010-Surface-Ownership]]"
owner: user:edwin
created: 2026-07-29
updated: 2026-07-29
source: []
parent: "[[FEAT-0048-Changes-On-The-Overview]]"
effort: S
depends: []
blocks: ["[[TASK-0240-Changes-Tile]]"]
related: ["[[TASK-0040-Changes-Hybrid-Buckets]]"]
tests: ["[[TST-0022-Surface-Ownership]]"]
---

# TASK-0239 — Changes payload

## Definition of Done
- [ ] `changes_payload(index)` returns recent items plus the bucketed remainder in one response
- [ ] `_changes_subgroups` is reused unchanged — no reimplementation of the hybrid bucketing
- [ ] Served at `GET /api/cockpit/changes`
- [ ] Bucket labels and membership match what Library rendered

## Steps
- [ ] Add `changes_payload` to `cockpit.py`, calling `_changes_subgroups` on the CHG records
- [ ] Split the first bucket (current week) out as `recent`; keep the rest as `buckets`
- [ ] Register the route in `server.py` beside the other `/api/cockpit/*` endpoints
- [ ] Test in `tests/test_overview_payloads.py`: bucket labels match the Library output for the same corpus

## Notes

The parity test against Library's grouping is worth having only until [[TASK-0245]] removes that group; after that it becomes a snapshot of the labels. Write it as a direct assertion on the labels rather than a comparison against the soon-to-be-deleted code path.
