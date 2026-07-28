---
type: "[[task]]"
id: TASK-0225
aliases: ["TASK-0225"]
title: "Design rationale — the ADRs a design links, not all of them"
status: backlog
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["[[FEAT-0043-Design-Top-Level-Surface]]"]
parent: "[[FEAT-0043-Design-Top-Level-Surface]]"
effort: "S"
depends: ["[[TASK-0223]]"]
blocks: []
related: []
tests: []
---

# Design rationale

## Definition of Done

- [ ] The surface lists ADRs reachable from a design note's `related:` / `implements:` links
- [ ] Governance ADRs that no design links do **not** appear
- [ ] Each entry states the decision in one line, and opens the ADR
- [ ] A design linking no ADRs shows nothing rather than an empty section

## Steps

- [ ] Resolve design → ADR through the existing link graph
- [ ] Render the list
- [ ] Test that an unlinked governance ADR stays out

## Notes

The filter is the whole task. [[ADR-0006]] (retire the delivered band) is design rationale; ADR-0011 (dated promotion) is process governance. Surfacing every ADR would drag governance into a product surface and bury the two or three that actually explain why something looks the way it does.

Resolution is through the **link graph**, not a title heuristic. An ADR title-substring match was tried once in the review desk and removed in independent review for exactly this reason: it guesses, and a guess that is usually right is worse than an explicit link, because nobody can tell when it is wrong.
