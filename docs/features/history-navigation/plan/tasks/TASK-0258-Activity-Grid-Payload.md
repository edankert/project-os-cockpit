---
type: "[[task]]"
id: TASK-0258
aliases: ["TASK-0258"]
title: "activity_payload — per-day transition and commit counts across the whole history, cached on HEAD"
status: done
phase: "[[PHASE-018-History-You-Can-Reach-And-Traverse]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["[[FEAT-0053-History-Navigation]]"]
parent: "[[FEAT-0053-History-Navigation]]"
effort: S
depends: []
blocks: ["[[TASK-0259-Contribution-Grid]]"]
related: ["[[TASK-0255-History-Payload]]"]
tests: []
---

# The activity payload

## Definition of Done
- [x] `GET /api/cockpit/activity` returns `{days: {"YYYY-MM-DD": {transitions, commits}}, first_commit, last_commit, buckets}`
- [x] `first_commit` is present so the grid can render pre-history as **absent** rather than as zero
- [x] `buckets` are the **quartiles of this repo's own active days**, computed server-side — the client must not invent a scale
- [x] Cached on HEAD; a new commit invalidates it and nothing else does
- [x] Every git failure degrades to `{"available": false}`, matching the two payloads beside it
- [x] Fixed argv, bounded timeout

## Steps
- [x] Reuse `_parse_history_log` — the same pass, aggregated by date instead of grouped by commit
- [x] Compute quartile thresholds over non-zero days only; a scale that includes the zeros is a scale where everything is dark
- [x] Test: counts against a fixture repo, thresholds against a known distribution, and the empty-repo case

## Notes

**Why not a field on the history payload.** That one is deliberately uncached — its uncommitted band must never be stale. This one *must* be cached: a full-history `-U0` pass is 0.57 s and 3.3 MB on this repo. Opposite requirements, so two endpoints; merging them forces one to be wrong.

**Quartiles over active days, not over the calendar.** With 16 active days in 365, including the zeros would put every threshold at 0 and every lit cell in the top bucket — the exact failure this replaces.

## Done 2026-07-30

`cockpit.activity_payload` + `GET /api/cockpit/activity`, cached on HEAD alone — the index generation is deliberately **not** in the key, because editing a note cannot change a past commit. Measured: **0.33 s cold, 0.00 s warm.**

Measured on this repo: 16 active days across 12 weeks, `first_commit: 2026-05-07`, `buckets: [22, 36, 64]`.

Those buckets are the point. Under GitHub's fixed 1/4/7/10 all sixteen active days would sit in the top step, because the median active day carries 34 transitions. With quartiles over active days the sixteen spread **5 / 4 / 3 / 4** across the four steps — verified in the running app.

Five tests, including one asserting the busiest day carries more transitions than commits: if those were equal the payload would be counting saves rather than completions.
