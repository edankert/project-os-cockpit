---
type: "[[task]]"
id: TASK-0313
aliases: ["TASK-0313"]
title: "The workspace card says since-when and how-many"
status: doing
phase: "[[PHASE-026-The-Returning-Human]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-10
source: ["[[FEAT-0071-Since-You-Looked]]"]
parent: "[[FEAT-0071-Since-You-Looked]]"
effort: S
depends: ["[[TASK-0312]]"]
blocks: []
related: []
tests: []
---

# The workspace card says since-when and how-many

## Definition of Done

- One line per workspace: `since Thu · 14 transitions · 2 need you`, derived from history_payload and the registers; NEEDS-YOU cards widen to anything-waiting.

## Groundwork landed 2026-08-10 — the payload, not the surface

`GET /api/cockpit/digest` exists: `cockpit.digest_payload()` returns the transitions since the watermark and the items that need a human, split — because that split is the point. **This task's renderer is not built**, and the task stays `backlog`.

Two decisions already taken in the payload, so the surface inherits rather than re-decides them:

- **It errs toward re-showing, never hiding.** `history_payload` reports commit dates at *day* granularity while the watermark is a timestamp, so a same-day commit cannot be ordered against a same-day watermark. The watermark's own day is therefore **included**: re-showing what was seen is corrected by reading, whereas hiding what came after catching up is invisible. Same asymmetry as the epoch default.
- **`computed_at` is what a `Caught up` should record**, not the moment the button is pressed — otherwise anything landing while the human reads is silently marked seen.

`needs_you` is deduplicated: an item owed for two reasons is still one thing to do — the rule the triage tray had to learn the hard way.

**Not a second obligation vocabulary.** `DIGEST_NEEDS_YOU` is one list in one module with one consumer, and it reads from [[FEAT-0089]]'s registry once that lands. If it outlives the registry it becomes exactly the drift [[ISS-0023]] describes.

## The registry swap landed 2026-08-10 — still not the surface

`DIGEST_NEEDS_YOU` is gone. `digest_payload` reads [[FEAT-0089]]'s registry through `_owed_flag`, which is what the paragraph above said to do once the registry existed.

**Measured, and the drift was already real:** the hand-written list held six types and omitted `change` (81 owed here) and `feature` (`acceptance: requested`), and had no way to express the `test` predicate's manual-only clause. A digest built from it would have told the returning human that 8 things needed them while the badges said 96. `test_the_digest_and_the_badges_count_the_same_things` now pins the two together — allowing exactly one gap, the standing documents, whose subject is a manifest entry rather than a note.

Every `needs_you` row also carries its `owed_verb` now, so the band this task builds can say *what* is owed rather than only that something is.

**The renderer is still not built.** This task stays `doing`: the line the DoD describes — `since Thu · 14 transitions · 2 need you`, one per workspace — needs a place on the rail that the 44px strip does not have, and choosing that place is the work, not typing it.
