---
type: "[[plan]]"
title: "Risks on the Issues surface — delivery plan"
status: done
owner: user:edwin
created: 2026-07-29
updated: 2026-07-29
implements: ["[[FEAT-0047-Risks-On-The-Issues-Surface]]"]
related: ["[[ISS-0063-Dead-Stat-Tiles]]"]
---

# Risks on the Issues surface — delivery plan

## Delivery sequence

1. **[[TASK-0237]]** — `_issues_groups` gains risk records, bucketed by the same `severity:` field, emitted as their own severity-ranked groups with a `risk` type on each item so the renderer's existing type icon distinguishes them.
2. **[[TASK-0238]]** — the overview's Risks stat tile is passed `'issues'` as its `navMode`, making it a button like Features/Tasks/Issues. One-line change that only becomes honest once step 1 lands.

## Sequencing note

Step 2 must not merge before step 1 — a tile that navigates to a mode not listing risks is a worse dead end than one that does nothing.
