---
type: "[[task]]"
id: TASK-0240
aliases: ["TASK-0240"]
title: "Changes tile in the overview history band — recent expanded, archive collapsed"
status: done
phase: "[[PHASE-010-Surface-Ownership]]"
owner: user:edwin
created: 2026-07-29
updated: 2026-07-29
source: []
parent: "[[FEAT-0048-Changes-On-The-Overview]]"
effort: M
depends: ["[[TASK-0239-Changes-Payload]]"]
blocks: ["[[TASK-0245-Drop-Relocated-Groups]]"]
related: ["[[TASK-0200-Overview-Stage-Rework]]"]
tests: ["[[TST-0022-Surface-Ownership]]"]
---

# TASK-0240 — Changes tile

## Definition of Done
- [ ] `buildChangesTile()` renders in the history band alongside Activity and Commits
- [ ] Recent changes expanded by default
- [ ] Older buckets render as collapsed disclosures beneath them, each opening to its rows
- [ ] Every bucket Library showed is reachable from the tile
- [ ] Rows navigate to the CHG note

## Steps
- [ ] Add the tile to `renderProjectOverview`'s parts list, after `buildActivityTile`
- [ ] Fetch `/api/cockpit/changes`; render recent rows directly
- [ ] Render each older bucket with the existing `ov-chev` disclosure pattern used by `buildRecordDisclosure`
- [ ] Best-effort: an older sidecar without the endpoint leaves the tile off rather than erroring

## Notes

Project scope only — the scoped (phase) overview keeps its own record column and is out of scope for this feature.
