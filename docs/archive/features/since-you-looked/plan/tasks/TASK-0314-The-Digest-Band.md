---
type: "[[task]]"
id: TASK-0314
aliases: ["TASK-0314"]
title: "The overview's digest band, needs-you lifted"
status: done
phase: "[[PHASE-026-The-Returning-Human]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-10
source: ["[[FEAT-0071-Since-You-Looked]]"]
parent: "[[FEAT-0071-Since-You-Looked]]"
effort: M
depends: ["[[TASK-0312]]"]
blocks: []
related: []
tests: []
---

# The overview's digest band, needs-you lifted

## Definition of Done

- A band atop the overview when the watermark is behind: transitions grouped as History groups them, needs-you items (triage, questions, acceptance, changes-requested) lifted above the informational; `Caught up` at its end.
- Reading to the bottom is what being caught up means — the button lives there, not in the header.

## Groundwork landed 2026-08-10 — the payload, not the surface

`GET /api/cockpit/digest` exists: `cockpit.digest_payload()` returns the transitions since the watermark and the items that need a human, split — because that split is the point. *(That was true when written. The renderer landed 2026-08-10 — see below.)*

Two decisions already taken in the payload, so the surface inherits rather than re-decides them:

- **It errs toward re-showing, never hiding.** `history_payload` reports commit dates at *day* granularity while the watermark is a timestamp, so a same-day commit cannot be ordered against a same-day watermark. The watermark's own day is therefore **included**: re-showing what was seen is corrected by reading, whereas hiding what came after catching up is invisible. Same asymmetry as the epoch default.
- **`computed_at` is what a `Caught up` should record**, not the moment the button is pressed — otherwise anything landing while the human reads is silently marked seen.

`needs_you` is deduplicated: an item owed for two reasons is still one thing to do — the rule the triage tray had to learn the hard way.

**Not a second obligation vocabulary.** `DIGEST_NEEDS_YOU` is one list in one module with one consumer, and it reads from [[FEAT-0089]]'s registry once that lands. If it outlives the registry it becomes exactly the drift [[ISS-0023]] describes.

## Done 2026-08-10

The band renders atop the overview when the watermark is behind, and is **absent** when it is not — a permanent *"nothing happened"* is the shape of thing a reader learns to stop seeing, which this surface has been taught twice.

Three of [[DES-0008]]'s decisions are now code, and each is pinned by a test because each is a one-word edit away from reversing:

- **Owed above news.** `needs_you` renders before `transitions`, marked. A reader who stops halfway should have seen the obligations, not the news — which is the entire reason `digest_payload` returns two lists rather than one sorted one.
- **`Caught up` at the foot.** *"Reading to the bottom is what being caught up means."* In the header it would be a dismiss control, and a dismiss control on a digest is a way to mark unread things read.
- **It records `computed_at`, not the click.** Anything that lands while the human is reading must not be marked seen. This is the most reversible decision in the feature — `new Date().toISOString()` is a one-word edit that loses work silently and looks identical on screen — so it has its own assertion.

### The row limit is a summary, not a fold

Eight rows per half, then *"+ N more — open History for the rest"*. Measured on this repo: an epoch watermark yields **440 transitions and 93 owed items**, which is a page nobody reads. History already holds everything and groups it the same way, so the band summarises rather than duplicating — no toggle, because a toggle would make it a second History.

### One mutation survived, and the test was the thing that was wrong

Swapping the two halves left `test_owed_items_are_lifted_above_the_news` passing. The assertion read `band.index("d.needs_you") < band.index("d.transitions")` — and `d.needs_you` also matches `d.needs_you_count` in the absent-band guard at the top of the function, so it was comparing the guard against the list and would have passed in either order. It asserts on the list bindings now.

That is the third test of mine this release's mutation pass has caught before the code, all the same shape: written to describe the decision rather than to trip on its reversal.
