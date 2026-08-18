---
type: "[[feature]]"
id: FEAT-0130
aliases: ["FEAT-0130"]
title: "A surface is a note, not a string retyped on every check — so an untested surface is visible rather than absent"
status: backlog
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
requirements: ["[[REQ-0049-A-Surface-Exists-Whether-Or-Not-A-Test-Names-It]]"]
tasks: ["[[TASK-0514-The-Surface-Note-Type]]", "[[TASK-0515-Consolidate-Your-Trainer-Surfaces]]", "[[TASK-0516-Surfaces-On-The-Design-View]]"]
related: ["[[DES-0012-Tests-In-Two-Flows]]"]
tags: [feature]
---

# A surface is a thing, not a string

Edwin: *"The surface ticket types are great but where should they be visible, probably in the design?"*

Today `area:` is **free text retyped on every check**. `your-trainer` has 76 distinct values for 579 checks, including `"Moved from Tier 1 / Tier 2 — Fully Automated"`, which is a migration bucket wearing a surface's clothes. Nothing can answer *which surfaces have no coverage*, because a surface only exists if a check happens to mention it.

A `SUR-*` note makes the surface exist first. Then:

- **An untested surface is visible** — a row with no checks, rather than nothing at all.
- **The suite groups by a controlled vocabulary** rather than by whatever was typed.
- **A release can report per surface**, which is what [[DES-0012]] D1 and the progress bars need.

## Where it is visible

**The design view**, per Edwin. That view already holds what bounds the project — ADRs, risks, the glossary — and a surface is exactly that: a standing statement of what the application *is made of*, independent of any one feature. Tests then reference it; the design view owns it.

## Consolidation is part of the feature, not after it

76 is not a vocabulary, it is a list. Edwin's own examples: `Per-Rider Data Export` → `Data Import/Export`; `Workout Loop/Repeat` → a generic `Workouts`; `HR Zone Lock` → `HR Zones`. The target is a set a person can hold in their head — roughly 12–15 for `your-trainer` — and the mapping is a judgement per area, recorded.

## Acceptance

- [ ] A `SUR-*` note type exists with a template and schema entry.
- [ ] `your-trainer`'s 76 areas map onto a consolidated set, each mapping recorded.
- [ ] Surfaces appear on the design view.
- [ ] A surface with no checks is visible as such.
