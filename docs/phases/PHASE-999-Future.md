---
type: "[[phase]]"
id: PHASE-999
aliases: ["PHASE-999"]
title: "Future / Unphased"
status: planned
order: 999
owner: user:edwin
created: 2026-05-23
updated: 2026-05-23
features: []
depends_on: []
---

# Phase 999: Future / Unphased

## Goal
Sentinel parking-lot phase. Holds any feature / task / requirement that hasn't been assigned to a concrete delivery phase yet — so nothing slips through the cracks of phase-aware tooling (PHASES.md registry, cockpit phase grouping, snapshot focus).

## Why a sentinel
Items without a `phase:` value disappear from phase-grouped views in the cockpit and aren't visible to phase-gated workflow checks. Rather than allow `phase: ""`, point at this phase. When the item gets serious planning, re-phase it into the concrete phase that will deliver it.

## Scope

### In scope
- Anything genuinely deferred without a target delivery phase yet.
- New ideas captured before triage decides which phase owns them.

### Out of scope
- Items that already have a clear phase home (use that phase).
- Cancelled / superseded work (mark with the relevant terminal status; do not re-phase here).

## Exit Criteria
PHASE-999 itself never "completes" — it stays open as a parking lot. Individual items leave by being re-phased.

## Notes
- The `order: 999` keeps it at the bottom of phase-sorted views without colliding with real phases.
- The `PHASE` counter in `SNAPSHOT.yaml` is NOT advanced for this sentinel (it stays at the highest concrete phase number issued). Next-up phases continue from there.
