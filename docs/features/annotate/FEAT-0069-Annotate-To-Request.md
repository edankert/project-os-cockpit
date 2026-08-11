---
type: "[[feature]]"
id: FEAT-0069
aliases: ["FEAT-0069"]
title: "Annotate to request — a pin or a selection on a design becomes a review-queue entry with an anchor that degrades honestly"
status: done
phase: "[[PHASE-025-Design-Before-Code]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[DES-0007-The-Bench-Closes-The-Loop]]"]
goal: "Click a rendered artefact or select design text, leave a comment, and a queue entry of kind `annotation` exists — anchored, listed under the design's desk entry, resolved through the existing resolve endpoint, and honest when its anchor no longer resolves."
requirements: []
tasks:
  - "[[TASK-0306-The-Annotation-Kind]]"
  - "[[TASK-0307-Pin-And-Selection-Capture]]"
  - "[[TASK-0308-Queue-Rendering-And-Honest-Anchors]]"
release: "[[REL-0001-The-Human-Has-Levers]]"
related: ["[[FEAT-0062-Desk-Resolution-Flows]]"]
tests: []
---

# Annotate to request

## Goal

Today the annotation channel is chat. The queue's `review-request` POST already takes a kind, a subject and a body; this adds `annotation` to its vocabulary, an anchor payload (variant + CSS path for pins, text quote for selections), and the bench-side capture. Anchors that stop resolving report "anchor lost at revision <sha>" — the `subject_missing` honesty rule, extended.

## Out of Scope

- Threads. An annotation is one observation; conversations are sessions.
- Annotating outside designs. If it earns its keep on the bench, widening is a later, cheaper decision.

## Acceptance

- [x] The queue understands `annotation` with a subject and an anchor, round-tripping through the store ([[TASK-0306]])
- [x] The anchor schema is an **allow-list** — a coordinate cannot be persisted under any name
- [x] A selection on a design becomes an annotation anchored to its quote; esc costs nothing ([[TASK-0307]])
- [x] Anchors are re-resolved at render as `found` / `moved` / `lost`, and **never float to the wrong spot** ([[TASK-0308]])
- [x] Resolution prefers the quote over the variant, so a renamed variant does not throw away a good anchor
- [x] Resolution goes through the existing resolve endpoint — no second lifecycle

## Verification

`tests/test_annotations.py` — 12 tests. The one that matters most asserts a coordinate is dropped from the anchor whatever it is called, because that is the failure `append_design_comment` already paid for once.
