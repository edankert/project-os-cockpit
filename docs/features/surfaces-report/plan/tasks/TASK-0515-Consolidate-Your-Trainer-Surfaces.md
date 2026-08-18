---
type: "[[task]]"
id: TASK-0515
aliases: ["TASK-0515"]
title: "Map your-trainer's 76 areas onto a set of 12-15 surfaces, recording each mapping"
status: doing
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
parent: "[[FEAT-0130-Surfaces-Are-A-First-Class-Type]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# Map your-trainer's 76 areas onto a set of 12-15 surfaces, recording each mapping

Edwin's own examples set the grain: `Per-Rider Data Export` → `Data Import/Export`; `Workout Loop/Repeat` → a generic `Workouts`; `HR Zone Lock` → `HR Zones`.

**Propose the mapping before applying it.** 579 checks change `area:`; the original string is preserved on each note (REQ-0049 criterion 4) so the consolidation is reversible by reading.

## The mapping — agreed with Edwin 2026-08-19

Edwin's axis, not mine: **what drives the target**, with each type carrying its own ride and editor. My earlier proposal merged nine areas into one `Workouts` surface of ~180 checks; this is the corrected one. *"Quick Ride"* and *"Zone Ride"* are the app's own words — 4 and 9 mentions in the corpus — and `editor` clusters inside `HR-Zone Structured` (11), which is what says the editor belongs to the workout type rather than being a surface of its own.

| surface | absorbs | ~checks |
| --- | --- | --- |
| **Route & Free Ride** | Route Workouts (54) + the free-ride part of Simulation Mode | ~70 |
| **HR · Zone Ride & Editor** | HR-Zone Structured Workouts (32), HR Zone Lock (13) | 45 |
| **Power · Quick Ride & Editor** | the ERG/slope part of Simulation Mode | ~30 |
| **General Workouts** | Workout Execution (9), Loop/Repeat (12), Workout Editor (3), AI Workout Builder (16) | 40 |
| **Workout Selection** | Workout Library & Favorites (4), Workout Domain Tabs (6) | 10 |
| **History** | History & Data Portability (5), Workout Personal Bests (11) | 16 |
| **Monetization & Licensing** | Monetization & Licensing | 27 |
| **Data Import/Export** | Per-Rider Data Export (14), Data Backup & Restore (9) | 23 |
| **Riders & Profiles** | Ghost Riders (15), Profile Management (9) | 24 |
| **Trainer Compatibility** | Trainer Compatibility Verification | 20 |
| **Localization** | Runtime Translate-on-Demand (11), Localization Infrastructure (6) | 17 |
| **Integrations** | Strava Integration | 13 |
| **Display & Layout** | UI & UX (4), Split-Screen & Multi-Window (3) | 7 |
| **Hardware & Connectivity** | Hardware Connectivity | 6 |
| **Training Metrics** | FTP Calculation | 1 |

**Fifteen**, at the top of [[REQ-0049]]'s 12–15 target, from 25 Tier 1 areas.

## Two things that are not renames

**`Simulation Mode`'s 44 checks split across two surfaces.** Route/free-ride and ERG/power both live in it — 11 free-ride, 14 ERG, 38 slope mentions. These need **assigning one at a time by reading them**. A keyword rule would mis-file silently, because *slope* appears both in route riding and in ERG resistance, and a rule that is wrong in a way nobody can see is worse than 44 reads.

**`History & Data Portability` spans two.** Assigned whole to **History** because that is the half its name leads with; the portability overlap with Data Import/Export is recorded here rather than resolved, so whoever meets it later knows it was a judgement and not an oversight.

## Calls made, open to reversal

- **AI Workout Builder → General Workouts**: it generates for all three target types, so it is not one of them.
- **HR Zone Lock → HR · Zone Ride**, not Monetization. Under Edwin's axis it is an HR surface carrying a licensing constraint, rather than a paywall wearing an HR name. This reverses my own earlier call.
