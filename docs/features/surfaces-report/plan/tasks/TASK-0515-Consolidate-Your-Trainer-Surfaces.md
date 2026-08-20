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
review_verdict: changes-requested
parent: "[[FEAT-0130-Surfaces-Are-A-First-Class-Type]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# Map your-trainer's 76 areas onto a set of 12-15 surfaces, recording each mapping

Edwin's own examples set the grain: `Per-Rider Data Export` → `Data Import/Export`; `Workout Loop/Repeat` → a generic `Workouts`; `HR Zone Lock` → `HR Zones`.

**Propose the mapping before applying it.** 579 checks change `area:`; the original string must stay recoverable ([[REQ-0049]] criterion 4) so the consolidation is reversible by reading.

*(**This sentence originally read "the original string is preserved on each note" and that is not what was built.** The migration overwrote `area:` in place and wrote the original nowhere — no field, no body line. What makes the consolidation reversible is the mapping recorded further down this note, and the criterion is reconciled rather than ticked on [[REQ-0049]]. Corrected 2026-08-20.)*

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

## The mapping as applied, recorded — 2026-08-20

**The table above is the *proposal*, and it is not what was applied.** **Thirteen of its fifteen surface names exist nowhere in `your-trainer`** — `Route & Free Ride`, `Power · Quick Ride & Editor`, `Trainer Compatibility` and ten others; only `Localization` survives verbatim and `Riders & Profiles` survives with a case change. The applied set is the fourteen Edwin approved plus `Not a product surface`, and the section below it records the *counts* of that pass without recording the *mapping*. So [[REQ-0049]] criterion 2 — *"every original area maps onto one, with the mapping recorded rather than inferred"* — was not met by this note until now, and the only copy of the mapping was an uncommitted working-tree diff in another repo. This section is that record.

**Basis, stated because this phase has been bitten four times by not stating it — and then stated WRONG, which is the fifth.** Recovered from `git diff` in `your-trainer` against **`49cf2ce9`**, the last commit before any part of the surface migration was committed.

*(**This paragraph originally called `49cf2ce9` `HEAD`. It is not, and it was not when the table was built.** `your-trainer`'s HEAD is `0dad8104`, committed 2026-08-20 20:57 — fifteen minutes before the commit that recorded this table — and it migrated `area:` on six notes. So a reader following the instruction *"diff against HEAD"* today gets **73 distinct originals over 573 notes**, not 76 over 579, and does not reproduce the table below. Found by independent review. The table is unchanged and needs no correction: re-derived against `49cf2ce9` it matches **cell for cell**, every count and every note id, with an empty symmetric difference. What was wrong was the word `HEAD`.)*

**And `49cf2ce9` is the right basis to record, not merely the one I happened to use.** It is the last state in which all **579** originals are recoverable from one place. Since then `0dad8104` committed six of them — `TST-0434`, `TST-0435` (`Add Rider with Zero Users`), `TST-0436` (`Empty Workout History`), `TST-0444`, `TST-0445`, `TST-0446` (`HRM State on User Switch`) — so those three rows are already in git history and the other 573 are still only in a working tree. At `HEAD` the corpus carries **76** distinct `area:` values over **579** notes in `docs/tests/acceptance/`, none of them empty; the working-tree figure of **94** quoted in the section above is the count *after* [[TASK-0517]] resolved the parking bay into recovered heading names, which is a different pass against a different base. Both numbers are right about different things, and only one of them is reversible: the parking bay's recovered names exist in no commit, so the durable original is the one at `HEAD`.

`TST-0015` and `TST-0018` — the two `level: acceptance` notes outside the directory — carry **no `area:` field at `49cf2ce9`** and gained `area: ""` in the working tree. They are not in this table because the migration did not touch them, which is the same two-check gap the correction above records.

### 75 of the 76 map one-to-one

| original `area:` at HEAD | surface | checks |
|---|---|---|
| Name-collision dialog button arrangement | App shell & UX | 1 |
| Settings Master/Detail + About Inline | App shell & UX | 6 |
| Split-Screen & Multi-Window | App shell & UX | 3 |
| UI & UX | App shell & UX | 4 |
| Auto-translate-on-import — translate-then-save with wait dialog | Data — backup/export | 6 |
| Backup Auto Backup Exclusions | Data — backup/export | 1 |
| Data Backup & Restore | Data — backup/export | 9 |
| Generalised backup overlay | Data — backup/export | 1 |
| ZWO Import | Data — backup/export | 4 |
| Cadence Coaching | Hardware | 8 |
| Compat-test must never leave the app stuck | Hardware | 4 |
| Display Smoothing & Cadence Filter | Hardware | 7 |
| Hardware Connectivity | Hardware | 6 |
| HRM Mid-Workout Reconnect | Hardware | 4 |
| HRM State on User Switch | Hardware | 3 |
| Per-Rider Cross-Rider Bleed | Hardware | 1 |
| Trainer Compatibility Verification | Hardware | 20 |
| Empty Workout History | History & analytics | 1 |
| History & Data Portability | History & analytics | 5 |
| Coaching Text Events | Integrations — AI | 4 |
| Strava Integration | Integrations — Strava | 13 |
| Strava Polish — Branding + Pills + Reconciliation | Integrations — Strava | 17 |
| Strava Retry Button Visibility | Integrations — Strava | 2 |
| Localization Infrastructure | Localization | 6 |
| Runtime translate model | Localization | 7 |
| Runtime Translate-on-Demand | Localization | 11 |
| AI Coach Tier Gating | Monetization | 2 |
| Backup Family-Tier Integrity | Monetization | 2 |
| Family License on Cold Start | Monetization | 3 |
| Free Ride Display Name | Monetization | 2 |
| Monetization & Licensing | Monetization | 27 |
| Paywall Features | Monetization | 1 |
| Tier-1 locale grammar — Dutch banner + corpus | Monetization | 3 |
| Add Rider with Zero Users | Riders & profiles | 2 |
| FTP Calculation | Riders & profiles | 1 |
| FTP Field Editing | Riders & profiles | 2 |
| New Rider Setup Dialog | Riders & profiles | 7 |
| Per-Rider Data Export | Riders & profiles | 14 |
| Per-Rider File Dispatch | Riders & profiles | 3 |
| Profile Management | Riders & profiles | 9 |
| Rider Card | Riders & profiles | 6 |
| Strava Cross-Rider Safety | Riders & profiles | 1 |
| Ghost Riders | Riding — routes | 15 |
| Pending Route Import Survives Process Death | Riding — routes | 3 |
| Route card overflow — Edit/Duplicate hidden, Rename for imported | Riding — routes | 4 |
| Route Data Robustness | Riding — routes | 1 |
| Route Workouts | Riding — routes | 54 |
| Slope-mode Route fallback honours forced RES | Riding — routes | 3 |
| Energy Decimal Consistency | Riding — simulation | 1 |
| ERG Free Ride Minimum Power | Riding — simulation | 2 |
| ERG Target Power Sync | Riding — simulation | 3 |
| Simulation Mode | Riding — simulation | 44 |
| Simulation Mode Replaces Resistance | Riding — simulation | 3 |
| Trainer SIM Capability Re-Check | Riding — simulation | 2 |
| Virtual Gear Range | Riding — simulation | 4 |
| Haptic Feedback on Interval Transition | Riding — structured | 2 |
| HR Zone Lock | Riding — structured | 13 |
| HR-Zone Controller Hardening | Riding — structured | 3 |
| HR-Zone Structured Workouts | Riding — structured | 32 |
| Ramp Intervals | Riding — structured | 1 |
| Workout Loop/Repeat | Riding — structured | 12 |
| AI Workout Builder | Workouts — authoring | 16 |
| Editor save/discard model | Workouts — authoring | 8 |
| Workout Domain Tabs | Workouts — authoring | 6 |
| Workout Editor | Workouts — authoring | 3 |
| Workout Library & Favorites | Workouts — authoring | 4 |
| Completion Overlay Resume | Workouts — execution | 3 |
| Power Deviation UI | Workouts — execution | 2 |
| Segment Power Labels | Workouts — execution | 2 |
| Segment Time Display | Workouts — execution | 1 |
| Session Metrics Display | Workouts — execution | 3 |
| SessionEndOverlay Row Alignment | Workouts — execution | 1 |
| Skip-Back Data Preservation | Workouts — execution | 3 |
| Workout Execution | Workouts — execution | 9 |
| Workout Personal Bests | Workouts — execution | 11 |

Total **513** checks. Every row is a rename: no original value on this list reaches two surfaces, so reversing it needs nothing but this table.

### The 76th fans out, so it is recorded per note

`Moved from Tier 1 / Tier 2 — Fully Automated` is the parking bay — one string covering **66** checks that had already been moved once, which is why it is the single original value that could not map to one surface. [[TASK-0517]] resolved each to a recovered heading name first; those names are in no commit, so what is durable is the note-by-note assignment:

| surface | checks | notes |
|---|---|---|
| App shell & UX | 1 | TST-0555 |
| Data — backup/export | 5 | TST-0537, TST-0538, TST-0539, TST-0558, TST-0582 |
| Hardware | 9 | TST-0553, TST-0563, TST-0578, TST-0592, TST-0593, TST-0594, TST-0595, TST-0596, TST-0597 |
| History & analytics | 3 | TST-0560, TST-0568, TST-0569 |
| Localization | 2 | TST-0548, TST-0549 |
| Monetization | 3 | TST-0561, TST-0565, TST-0573 |
| Not a product surface | 2 | TST-0571, TST-0577 |
| Riders & profiles | 10 | TST-0554, TST-0559, TST-0562, TST-0567, TST-0575, TST-0583, TST-0584, TST-0585, TST-0586, TST-0587 |
| Riding — routes | 11 | TST-0541, TST-0542, TST-0543, TST-0545, TST-0572, TST-0580, TST-0581, TST-0588, TST-0589, TST-0590, TST-0591 |
| Riding — simulation | 1 | TST-0534 |
| Riding — structured | 9 | TST-0532, TST-0535, TST-0536, TST-0540, TST-0552, TST-0556, TST-0557, TST-0564, TST-0579 |
| Workouts — authoring | 9 | TST-0544, TST-0546, TST-0547, TST-0550, TST-0551, TST-0566, TST-0570, TST-0574, TST-0576 |
| Workouts — execution | 1 | TST-0533 |

Total **66**. 513 + 66 = **579**, which is the number of notes the migration rewrote.

### The surfaces themselves are in no commit, anywhere

Disclosed after independent review, because nothing above said it and every claim here depends on it: `git log --all -- 'docs/surfaces/*'` in `your-trainer` returns **nothing**. The fifteen `SUR-*` notes have never been committed on any branch, and neither has the `area:` rewrite of the other 573 checks. **At `your-trainer`'s HEAD that repo has zero surfaces and 579 checks naming none of them.**

So this whole migration is a working tree. That does not weaken the record — it is the reason the record was worth making, since a `git checkout` there would take the mapping with it — but it does bound every downstream claim, and the notes that made those claims now say so ([[FEAT-0130]], [[ISS-0250]]).

### What this record does and does not do

It makes the consolidation **reversible by reading**, which is what [[REQ-0049]] criterion 4 protects: for any of the 579 checks, the original string is recoverable from one of the two tables above without opening a diff. What it does **not** do is put the original *on the note*, which is what that criterion literally asks for — see the reconciliation recorded on [[REQ-0049]].


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

## Independent review — fresh-context pass, 2026-08-20 (`b4b9c50` / `4521a7a`)

Separate session, `model:claude-opus-5`, starting from the notes and the diff with no access to the author's reasoning. Same model family as the author, recorded in `reviewed_by`; the independence claimed here is **context**, not weights ([[project-os-dev#ADR-0013]]).

**Verdict: changes-requested.** The mapping is exact. Its stated basis is not.

### The table was re-derived from scratch and is correct in every cell

Independently reconstructed by parsing `area:` out of every note in `docs/tests/acceptance/` at `49cf2ce9` and joining per file against the working tree, without reading this note's table first:

- **580** files, **579** notes once `README.md` is excluded; **76** distinct `area:` values, none empty; **15** in the working tree.
- **75** originals map one-to-one, totalling **513** checks. Compared row by row against the table above: **zero** rows missing, zero extra, zero disagreements on surface or on count.
- The 76th fans across **13** surfaces over **66** checks, and every note ID in the second table matches — all thirteen rows, all 66 IDs.
- 513 + 66 = **579**. Confirmed.
- *"Thirteen of its fifteen proposal names exist nowhere"* — confirmed for the applied surface set: only `Localization` survives verbatim, `Riders & Profiles` survives as `Riders & profiles`, and the other thirteen match no applied surface under any casing.

### BLOCKING — the basis is mislabelled, and the reason given for it is false

*"Recovered from `git diff` in `your-trainer` against **`HEAD`** (`49cf2ce9`), which is where the original strings still are — the migration is uncommitted there."*

`49cf2ce9` is dated 2026-08-18 15:44 and was **not** `HEAD` when this was written. `your-trainer`'s `HEAD` was `0dad8104`, committed 2026-08-20 **20:57** — fifteen minutes before `b4b9c50` at 21:12 — with four further commits in between.

And `0dad8104` is *"TST-0434 TST-0435 TST-0436 TST-0444 TST-0445 TST-0446: name the feature each check verifies"*, which **committed the migrated `area:` on six notes**. So *"the migration is uncommitted there"* is false for `TST-0434`, `TST-0435`, `TST-0436`, `TST-0444`, `TST-0445` and `TST-0446`.

The consequence is concrete rather than pedantic. Re-deriving the same table against the real `HEAD` gives 75 one-to-one rows again, but **three different keys**: `Riders & profiles` (2), `History & analytics` (1) and `Hardware` (3) stand where `Add Rider with Zero Users`, `Empty Workout History` and `HRM State on User Switch` are recorded here. A reader who follows this note's own instruction today does not reproduce this table.

It cuts both ways, and the better half is worth stating: those three original strings now survive **only** in this table and in commits before `0dad8104`. The record is more load-bearing than the note claims, not less. What needs correcting is the sentence — name `49cf2ce9` as the basis it is, drop *"HEAD"*, and drop *"the migration is uncommitted there"*.

The same stale basis carries into [[FEAT-0132]] (recorded there) and into [[REQ-0051]]'s fleet pair.
