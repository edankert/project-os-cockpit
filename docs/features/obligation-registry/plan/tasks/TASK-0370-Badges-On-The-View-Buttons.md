---
type: "[[task]]"
id: TASK-0370
aliases: ["TASK-0370"]
title: "Each view button carries its own owed count, and together they cover every kind"
status: backlog
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-10
updated: 2026-08-10
source: ["[[ADR-0020-Obligations-Live-With-Their-Subject]]"]
parent: "[[FEAT-0089-The-Obligation-Registry-And-The-Badges]]"
effort: S
due: ""
depends: ["[[TASK-0369-The-Obligation-Registry]]"]
blocks: []
related: ["[[DES-0008-The-Returning-Human]]", "[[DES-0002-Cockpit-Design-System]]"]
tests: []
---

# Badges on the view buttons

## Definition of Done
- [ ] Every view button shows its owed count; absent, not zero, when nothing is owed
- [ ] The badges sum to the registry total — asserted, so a kind cannot be added without appearing somewhere
- [ ] The badge updates on the SSE event that re-renders its surfaces; no optimistic state
- [ ] It reads at the top bar's size without crowding the icon, in both themes

## Steps
- [ ] Consume the registry's per-view counts
- [ ] Style per [[DES-0002]] — existing chip tokens, no new palette
- [ ] Assert the sum in a test, over a fixture with at least one kind per view

## Notes
This is the whole replacement for the desk's one number, and it is a better answer: continuous rather than on visit.

**Watch the change badge.** 76 unreviewed CHG notes would make the Overview read `76` beside four single-digit views. That number is accurate and it is real debt with a deadline — but it may drown the kinds that are actionable today. The cutoff parameter from [[TASK-0369]] is where that is settled; do not quietly clamp or hide it in the renderer, which would be a display lying about a gate.
