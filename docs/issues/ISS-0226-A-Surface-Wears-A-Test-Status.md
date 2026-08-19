---
type: "[[issue]]"
id: ISS-0226
aliases: ["ISS-0226"]
title: "A surface row carries `ready`/`passing` — the runner's vocabulary, borrowed for a thing that is not a test and cannot pass"
status: fixed
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
severity: medium
component: cockpit-desktop
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[ISS-0225-A-Nav-Row-Carries-Data-No-Renderer-Draws]]", "[[ADR-0034-Three-Axes-Not-One-Word]]", "[[TASK-0550-The-Nav-Groups-By-Surface]]"]
---

# Borrowed vocabulary

Edwin, 2026-08-19: *"what does ready and passing mean for them?"*

**Nothing, and that is the defect.** `_surface_rows` emits `status: "passing" | "ready"` because it was written from the shape of the row it replaced — a *check* row, where those values come from `statuses.VOCABULARY` and describe test execution.

A surface is a place in the application. It is not run, it does not pass, and it is never ready. `passing` on it is a category error that reads as a claim.

It is also a **second encoding of the bar**: both say how much of the surface is settled, and this whole phase has been about removing exactly that.

## Suggested fix

**A surface carries no status.** The bar is its state, and one fact should have one encoding ([[ADR-0032]]'s rule, applied to a nav row).

If a signal beyond the bar is wanted, it must mean something about a *surface* rather than about a runner — *complete*, *has stale evidence*, *owed* — and it must not reuse a value the test vocabulary already owns, because `statuses.VOCABULARY` is what decides whether a surface ranks as open work elsewhere.

## Done when

- [x] A surface row emits no test status.
- [x] Whatever it does emit is not a value `statuses.VOCABULARY` defines, or it is one deliberately and the note says why.
