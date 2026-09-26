---
type: "[[task]]"
id: TASK-0370
aliases: ["TASK-0370"]
title: "Each view button carries its own owed count, and together they cover every kind"
status: done
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
- [x] Every view button shows its owed count; absent, not zero, when nothing is owed
- [x] The badges sum to the registry total — asserted, so a kind cannot be added without appearing somewhere
- [x] The badge updates on the SSE event that re-renders its surfaces; no optimistic state
- [x] It reads at the top bar's size without crowding the icon, in both themes

## Steps
- [x] Consume the registry's per-view counts
- [x] Style per [[DES-0002]] — existing chip tokens, no new palette
- [x] Assert the sum in a test, over a fixture with at least one kind per view

## Notes
This is the whole replacement for the desk's one number, and it is a better answer: continuous rather than on visit.

**Watch the change badge.** 76 unreviewed CHG notes would make the Overview read `76` beside four single-digit views. That number is accurate and it is real debt with a deadline — but it may drown the kinds that are actionable today. The cutoff parameter from [[TASK-0369]] is where that is settled; do not quietly clamp or hide it in the renderer, which would be a display lying about a gate.

## Done 2026-08-10

`GET /api/cockpit/obligations` and a badge on each view button. **Absent, never zero** — a permanent `0` is the shape of thing a reader learns to stop seeing, and this surface has been taught that twice.

Measured on this corpus: `overview 81 · issues 7 · features 5 · intent 1 · tests 0`, total **94**.

`test_the_badges_sum_to_the_registry_total` asserts the total equals the sum, because a total that disagrees is exactly how a kind goes missing without anyone noticing. `test_every_owed_note_lands_in_exactly_one_view` asserts no note is counted twice — counting one twice is as wrong as missing it.

### The change badge reads 81, and it is not clamped

[[ADR-0020]]'s amendment predicted this: *"a badge reading 76 may drown the four kinds that are actionable today."* It is 81 now, against 7 · 5 · 1 · 0 elsewhere — so the concern was real and is live.

**It is deliberately not clamped, and a test forbids clamping it.** `test_the_renderer_reads_the_count_and_declares_no_kinds` fails on `Math.min`, `> 99` or `'99+'` in the badge. Those changes are real debt with a deadline of 2026-10-23, and hiding the number in the renderer would be a display lying about a gate. Whether the historical ones count is a **cutoff parameter** for Edwin, left open in [[ISS-0128]] — and it belongs in `obligations.py`, not behind a display clamp.

### One mapping, in one place

The registry's view names are the server's (`intent`); the buttons' `data-mode` values are the renderer's (`design`, still, until [[FEAT-0087]] renames it). The mapping lives in the renderer — so the server never learns about `design` and the renderer never learns about obligation states, which the test also asserts.
