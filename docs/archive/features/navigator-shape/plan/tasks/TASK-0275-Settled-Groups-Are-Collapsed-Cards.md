---
type: "[[task]]"
id: TASK-0275
aliases: ["TASK-0275"]
title: "A group whose every item is terminal renders shut, with its count in the head — the context card's behaviour, in the navigator"
status: done
phase: "[[PHASE-022-Completed-Work-Gets-Quieter]]"
owner: user:edwin
created: 2026-08-02
updated: 2026-08-02
source: ["[[FEAT-0058-One-Shape-Per-Navigator]]"]
parent: "[[FEAT-0058-One-Shape-Per-Navigator]]"
effort: S
depends: []
blocks: ["[[TASK-0276-The-Divider-Where-Names-Do-Not-Say-Finished]]"]
related: ["[[TASK-0274-The-Context-Pane-Becomes-Record-Cards]]"]
tests: ["[[TST-0023-Completed-Work-Ordering]]"]
---

# Settled groups are collapsed cards

## Definition of Done

- A group with no open work opens **shut**; one with open work opens **open**. Exactly `renderContextGroup`'s rule, which is why the right pane reads the way Edwin likes.
- The head keeps its count and status (`Done · 265`), so a shut card still says what is in it.
- The server's `default_open: false` still wins where it is sent — this adds a reason to close, never a reason to open.
- Both surfaces.

## What this alone achieves

The tasks navigator, complete. Its groups are named `Done`, `Cancelled`, `Superseded`, so three collapsed cards *are* the completed section — no divider needed, which is exactly what Edwin specified.

## Verification

The tasks navigator shows five heads and no item rows until one is opened.
