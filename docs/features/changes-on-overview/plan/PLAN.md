---
type: "[[plan]]"
title: "Changes on the overview — delivery plan"
status: done
owner: user:edwin
created: 2026-07-29
updated: 2026-07-29
implements: ["[[FEAT-0048-Changes-On-The-Overview]]"]
---

# Changes on the overview — delivery plan

## Delivery sequence

1. **[[TASK-0239]]** — `changes_payload()` in `cockpit.py`, reusing `_changes_subgroups` unchanged, served at `GET /api/cockpit/changes`. Recent items and bucketed older items in one response so the tile makes a single fetch.
2. **[[TASK-0240]]** — `buildChangesTile()` in the renderer, appended to the history band; recent rows expanded, buckets as collapsed disclosures using the existing `ov-chev` pattern.

## Note

The bucketing logic is not rewritten. `_changes_subgroups` is lifted as-is and its output re-shaped at the payload boundary — the three tasks that tuned those buckets are why the archive is readable at all.
