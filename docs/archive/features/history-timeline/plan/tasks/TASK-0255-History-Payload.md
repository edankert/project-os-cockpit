---
type: "[[task]]"
id: TASK-0255
aliases: ["TASK-0255"]
title: "history_payload — status transitions from git, grouped by commit, with the uncommitted band on top"
status: done
phase: "[[PHASE-016-The-Overview-Answers-Questions]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["[[FEAT-0052-History-Timeline]]"]
parent: "[[FEAT-0052-History-Timeline]]"
effort: M
depends: []
blocks: ["[[TASK-0256-History-Tile-On-The-Overview]]", "[[TASK-0257-Full-History-View]]"]
related: ["[[TASK-0199-Commits-As-Documentation-Events]]"]
tests: []
---

# The history payload

## Definition of Done
- [x] `GET /api/cockpit/history` returns commits newest-first, each carrying the **status transitions** its diff contains — id, type, from, to, and the note's path
- [x] A transition distinguishes **created-at** from **moved-to**: a `+status:` with no matching `-status:` in the same file diff is a new note, not a change
- [x] An **uncommitted** band lists notes whose working-tree state differs from HEAD, so "not saved yet" is answerable
- [x] A commit with no transitions is **still present**, flagged — it does not vanish for having no rows
- [x] Every git failure mode degrades to `{"available": false}` rather than raising, matching `commits_payload`
- [x] Fixed argv, bounded timeout, clamped limit — the same hardening `commits_payload` carries

## Steps
- [x] One `git log -U0 --format=… -- docs/ SNAPSHOT.yaml` pass, parsed for `+++ b/<path>` and `±status:` pairs
- [x] One `git status --porcelain -- docs/ SNAPSHOT.yaml` for the uncommitted band
- [x] Resolve each path to its note through the live index, as `commits_payload` already does, so a row carries id/type rather than a filename
- [x] Test: a fixture repo with a created note, a moved note, a touched-but-unchanged note and an empty commit produces exactly the expected shape

## Notes

**Cheap, measured.** One `git log -U0 -- docs/` yields every `+status:` line with its commit in **0.08 s across 40 commits**. There is no caching problem to solve here; the existing commits cache pattern covers it if one appears.

**The created-vs-moved distinction is not pedantry.** Most notes in a busy commit are *born* `done` — written and closed in the same pass — and rendering that as `→ done` implies a journey the note never took. `PLAN.md` files are the clearest case: they arrive `active` and stay there.

**Why `SNAPSHOT.yaml` is included:** it is where the metrics live, and a commit that moved only the snapshot is still a documentation event. It carries no `status:` lines of its own, so it contributes to the divider, not to rows.

## Done 2026-07-30

`cockpit.history_payload` + `GET /api/cockpit/history`. One `git log -U0 -- docs/ SNAPSHOT.yaml` parsed for `+++ b/<path>` and `±status:` pairs, plus one `git status --porcelain` for the uncommitted band. Measured at ~0.08 s for 40 commits.

**Deliberately not cached.** `/api/cockpit/commits` caches on `(HEAD, index generation, limit)`; doing the same here would serve a stale "not committed yet" list — the one part of this payload whose entire value is being current. There is nothing a cache would rescue at this cost.

**`_parse_history_log` is split out** so the parsing can be exercised on log text rather than through a fixture repo per case. Parsing is where this can be wrong, and a repo per case would make the suite slow enough that nobody adds cases to it.

### Verified against real history

```
04069e3  6 transitions   FEAT-0051 new·done, PHASE-016 new·done, TASK-0252/3/4 new·done
cebee80  4 transitions   ISS-0074 new·fixed, PHASE-014/015 new·done, CHG new·merged
8953c6e  0 transitions   [UNDOC]  PHASE-013 review: fix the two guards…
f6e8781  5 transitions   FEAT-0044 doing→done, ISS-0072 open→fixed, PHASE-013 active→done
```

`cebee80` is the measurement the design rests on: it **touched 20 notes and changed 4 statuses**. The old commits tile shows 20 items for it. `8953c6e` correctly survives with zero rows and the flag.

Eleven tests. Mutation-verified on the two load-bearing behaviours: dropping zero-transition commits, and treating a created note as a move.
