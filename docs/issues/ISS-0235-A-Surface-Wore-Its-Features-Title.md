---
type: "[[issue]]"
id: ISS-0235
aliases: ["ISS-0235"]
title: "A Tier 1 surface rendered the title of the feature its checks cover — `covers:` is what a check verifies, not what the surface is"
status: fixed
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
severity: high
component: cockpit-desktop
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[ISS-0231-The-Surface-Row-Is-Two-Lines-And-Names-The-Wrong-Thing]]", "[[ISS-0226-A-Surface-Wears-A-Test-Status]]", "[[DES-0012-Tests-In-Two-Flows]]"]
---

# The feature's name where the area's belongs

Edwin, 2026-08-19: *"The left hand pane Feature tests still seems to somehow show the features and not the areas??"*

Measured in `your-trainer` before fixing:

| area | rendered as |
| --- | --- |
| `Profile Management` | **User Management** (`FEAT-0002`) |
| `AI Workout Builder` | **AI Training Partner** (`FEAT-0010`) |

## Cause

[[ISS-0231]] added `_surface_ref` so a **regression** row could carry its issue — Tier 2's areas are past bugs, and `TESTING.md` says each Tier 2 test references the `ISS-*` that created it. It resolved *any* ref every check in the surface shared, and for Tier 1 that is the `FEAT-*` they all `covers:`. The renderer then does `ref_title || title`, so the feature's title replaced the area's name.

**Two relations conflated.** `covers:` is **what a check verifies**. It is not **what the surface is**. A Tier 2 surface *is* an issue; a Tier 1 surface is a place in the application that happens to verify a feature. Substituting one title for the other is the same category error as giving a surface a runner's status ([[ISS-0226]]) — a value borrowed from a relation that looked close enough.

It did not show here because this repo's Tier 1 areas span several features, so no single ref is shared and the intersection came out empty. **A defect invisible in the repo it was written in and live in the one with the data** — the same shape as [[ISS-0219]] and [[ISS-0221]].

## Fixed 2026-08-19

`_surface_ref` resolves **only `ISS-*`**, which makes the title substitution safe by construction: `ref` can then only ever be an issue.

- [x] Tier 1 shows the area's own name.
- [x] Tier 2 shows `[ISS-*] <the issue's title>`.
- [x] Guarded: a surface's `ref` is an issue or absent, asserted against both repos.
