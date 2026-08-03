---
type: "[[feature]]"
id: FEAT-0069
aliases: ["FEAT-0069"]
title: "Annotate to request — a pin or a selection on a design becomes a review-queue entry with an anchor that degrades honestly"
status: planned
phase: "[[PHASE-025-Design-Before-Code]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[DES-0007-The-Bench-Closes-The-Loop]]"]
goal: "Click a rendered artefact or select design text, leave a comment, and a queue entry of kind `annotation` exists — anchored, listed under the design's desk entry, resolved through the existing resolve endpoint, and honest when its anchor no longer resolves."
requirements: []
tasks: []
release: ""
related: ["[[FEAT-0062-Desk-Resolution-Flows]]"]
tests: []
---

# Annotate to request

## Goal

Today the annotation channel is chat. The queue's `review-request` POST already takes a kind, a subject and a body; this adds `annotation` to its vocabulary, an anchor payload (variant + CSS path for pins, text quote for selections), and the bench-side capture. Anchors that stop resolving report "anchor lost at revision <sha>" — the `subject_missing` honesty rule, extended.

## Out of Scope

- Threads. An annotation is one observation; conversations are sessions.
- Annotating outside designs. If it earns its keep on the bench, widening is a later, cheaper decision.
