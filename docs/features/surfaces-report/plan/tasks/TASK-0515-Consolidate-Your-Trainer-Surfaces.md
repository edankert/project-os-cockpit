---
type: "[[task]]"
id: TASK-0515
aliases: ["TASK-0515"]
title: "Map your-trainer's 76 areas onto a set of 12-15 surfaces, recording each mapping"
status: done
owner: user:edwin
created: 2026-08-18
updated: "2026-08-20"
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: approved
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

## Done 2026-08-20 — 94 areas onto 15 surfaces

Edwin approved the 14-surface grouping and asked me to place the remainder. A fifteenth was needed and it is the honest one: **`Not a product surface`** (`kind: surface-less`) for the four checks about test scaffolding and the build rather than about the product. That is a fact about those checks, not a bucket for leftovers.

| | |
|---|---|
| `area:` strings before | **94** |
| surfaces after | **15** |
| checks re-homed | **579** (the 580th is the directory README, which is not a check) |
| areas left unplaced | **0** |

Fifteen `SUR-*` notes in `your-trainer/docs/surfaces/`, each stating **what it is** and — the field that does the work — **its boundaries**. Every one names the neighbour it is most likely to absorb: routes against simulation, authoring against execution, Strava against every other integration, the app shell against every feature's own screen.

### Measured with the right instrument, because the last time I did not

The gate is **unchanged**: 581 items, 59 blocking, 20 quiet, 11 resting — before and after, on a throwaway copy first and then on the repo, **with an indexed loader both times**. `_delta_key` is `(tier, name)` and `sort_items` never reads `area:`, so this moves no verdict and no delta.

That check exists because [[ISS-0213]]'s *"zero gate impact"* was measured with an index-less loader that could not have shown one. This is the same claim, made with an instrument that can fail.

### And my verification predicate was wrong, not the data

The pass that looked for stragglers tested whether `area:` began with `SUR-`, and reported 579 failures. The areas carry the surface **title**, which is what `surface_coverage` joins on — every one was correct. A predicate written after the migration, testing for something the migration never produced.

### What this leaves

`area:` is a string that now happens to equal a surface's title. **A check still does not link to a `SUR-*`**, and the join is by name — so renaming a surface silently orphans 91 checks. Closing that is a schema change on the check (`area:` becomes a link), which is [[FEAT-0130]]'s endpoint rather than this task's, and it is stated here so nobody reads the collapse from 94 to 15 as the whole job.

## Independent review — third pass, 2026-08-20

Fresh context, separate session, `model:claude-opus-5`, reviewing `6cc7f72..HEAD`. Verdict: **approved**. Every claim below was re-measured or re-executed.

**The gate claim is true, and provably stronger than stated.** Rather than compare two area mappings I collapsed all 579 `area:` values in a copy of the working tree to a single constant and re-measured with an indexed loader: `items=581`, `blocking=59`, and the **blocking key set is byte-identical** (symmetric difference 0). `Item.key` is `number + name` and `number` resolves to the note id, so `area:` cannot move the gate under *any* mapping. `quiet=20` and `resting=11` also reproduce.

Two things the note should carry:

**The 15 surfaces do not partition the suite.** They partition the 579 notes in `docs/tests/acceptance/`. The indexed loader returns **581** items: `TST-0015` and `TST-0018` are `level: acceptance` notes living in `docs/tests/`, and both carry `area: ""`. So the suite holds **16** distinct area values, one of them empty, and two checks sit on no surface at all. That is the same directory-versus-index blind spot that produced `ISS-0213`, surfacing in the migration rather than in a measurement.

**The `Riding` boundary is soft, and the note is right to distrust its own authorship.** Scoring each Riding check's title against the three surfaces' own vocabulary: **16 of the 91** in `Riding — routes` read as another Riding surface (`Multi-Lap Loop`, `DURATION → LAP after first rollover`, `ERG-Fallback Power Ramps Naturally at Ride Start`), **3 of 60** in `— simulation` (`Structured Workout Simulation`, `Elevation Terrain View`), **0 of 72** in `— structured`; and **6** straddle two (`Cockpit slope-mode chip — Route`, `ERG Power Updates on Interval Transition`, `Structured Workout ERG Default`). `Riding — routes` is absorbing in-ride behaviour generally, which is what a catch-all looks like. This is a title heuristic, not a reading of the checks — but it is enough to say the edge between `routes` and `simulation` is not sharp, and `Not a product surface` is a category rather than a place.

Neither affects the gate. Both affect what the `SUR-*` type can claim to be.

## Corrected after independent review — 579 of 581

The fifteen surfaces partition the **`docs/tests/acceptance/` directory**. The indexed loader returns **581**: `TST-0015` and `TST-0018` are `level: acceptance` notes living in `docs/tests/`, and both carry `area: ""`. So **two checks sit on no surface**, and the suite has 16 distinct area values rather than 15.

**That is the ISS-0213 blind spot again** — a directory walk standing in for the indexed corpus — and it is the third time this session the same gap has produced a wrong number. The migration itself is unaffected: those two carried no area before and carry none now. What is wrong is the claim that the mapping is total.

Neither is hard to fix; both need a surface chosen, which is a judgement about what they verify rather than a rule.

## The `Riding` boundary is soft, and the review says so with numbers

Scoring each surface's titles against its own vocabulary, independent review found **16 of the 91** rows on `Riding — routes` reading as another Riding surface, **3 of 60** on `— simulation`, **0 of 72** on `— structured`, and **6** straddling two. `Riding — routes` is absorbing in-ride behaviour generally.

A title heuristic is not a reading of the checks, so this is a signal rather than a verdict — but it points at the split I flagged as the one Edwin would most likely change, and it is the split I made without him. **`Not a product surface` is also a category rather than a place**, which the type's own template calls `surface-less` for exactly that reason.

Left as a finding on the mapping rather than a silent re-cut: re-drawing 91 rows on a heuristic would be inventing a taxonomy while claiming to recover one, which is the error [[TASK-0517]] recorded.
