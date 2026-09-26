---
type: "[[task]]"
id: TASK-0306
aliases: ["TASK-0306"]
title: "The queue learns `annotation`, with an anchor schema"
status: done
phase: "[[PHASE-025-Design-Before-Code]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[FEAT-0069-Annotate-To-Request]]"]
parent: "[[FEAT-0069-Annotate-To-Request]]"
effort: S
depends: []
blocks: []
related: []
tests: []
---

# The queue learns `annotation`, with an anchor schema

## Definition of Done

- review-request accepts kind `annotation` with subject + anchor (variant + CSS path + offset, or text quote); the store round-trips it; the ledger records it like any request.

## Done — 2026-08-11

`annotation` joins `KINDS`, and the anchor is an **allow-list** — `variant`, `path`, `quote` and nothing else.

**The allow-list is the point, not a formality.** `append_design_comment` already learned this: *"the anchor is a region id, never a coordinate. Pixel pins die on the next revision, and the founding artifact went through six in one session."* `normalise_anchor` drops `{x, y, top}` whatever they are called, so a coordinate cannot be smuggled in and quietly persisted as a pin.

Round-trips through the store and appears in the ledger like any request. An unknown kind is still refused — widening `KINDS` did not widen it to anything.

**One drift caught by widening it.** The endpoint carried its own literal `("review", "question")`, so `annotation` would have been refused at the door with the store perfectly capable of holding it. It now reads `review.KINDS` — the two-lists failure [[ISS-0023]] is about, found by making the list longer.
