---
type: "[[issue]]"
id: ISS-0164
aliases: ["ISS-0164"]
title: "Phases are the second note type the quick palette cannot find — 34 notes, the same defect [[ISS-0142]] described for releases and claimed was the only one"
status: "fixed"
phase: "[[PHASE-026-The-Returning-Human]]"
owner: user:edwin
created: 2026-08-14
updated: "2026-08-14"
source: ["Found while fixing [[ISS-0142]], 2026-08-14 — the per-type reachability measurement that verified the release fix reported a second type at zero"]
severity: low
component: navigation
parent: ""
related: ["[[ISS-0142-The-Release-Note-Cannot-Be-Found-By-Name]]", "[[FEAT-0072]]", "[[ISS-0132]]"]
tests: []
---

# Phases are the second type the palette cannot find

## What was found

[[ISS-0142]]'s title calls releases *"the one note type the quick-switch corpus has never carried"*. That was measured by hand, one type at a time. Measuring **every** type at once, while verifying its fix:

| type | notes | findable by id |
|---|---|---|
| task | 417 | 417 |
| issue | 163 | 163 |
| feature | 100 | 100 |
| requirement | 36 | 36 |
| adr / design / risk / decision | 36 | 36 |
| release *(fixed 2026-08-14)* | 1 | 1 |
| **phase** | **34** | **0** |

Typing `PHASE-011` into the bar reading *"Search files, IDs, or commands…"* returns **No matches**, for the same reason `REL-0001` did: `QUICK_CORPUS_MODES` is `features`, `issues`, `intent`, `library`, and no nav mode carries phases.

## Correction, 2026-08-14 — the cause above is wrong (Edwin: *"are phases not selectable on the Features page?"*)

**The `features` mode does carry phases.** `_features_groups` groups every feature under its phase and emits the group with `key` = the phase id, `label` = `PHASE-011 · Title`, `url` = `index.url_for(phase_record.path)` and the phase's own `status`. [[ISS-0132]] then made that head **navigate**: the label opens the note, the chevron folds, and `refreshActiveNavRow` highlights the selected phase like a selected feature. So a phase is reachable, selectable, and one click from the navigator — the sentence *"no nav mode carries phases"* is false.

**What is actually broken is one function.** `flattenNavItems` — the corpus builder behind `Cmd+P` — walks `group.items` and `group.subgroups` and **never the group header itself**. So the 34 phases sit in a payload the palette already fetches, in the one field it does not read. That is why `rel.includes(q)` does not save them either, and why the count was a clean zero rather than a partial.

**This dissolves the question the issue was filed to ask.** There is no *where* to decide: phases already have a nav home and it is the right one, the plan's spine over the plan's tree. The fix is in the corpus builder — harvest a group that names a note — and it generalises, since any future mode that groups by an id-bearing note becomes findable for free rather than becoming the next `ISS-0142`.

## Options — superseded by the correction above

*Kept as filed, because all three assume phases have no nav home and that assumption is what was wrong. They are what a reader would think of first, which is the reason to leave them visible.*

1. ~~**A third explicit fetch** beside the two `buildQuickCorpus` already carries for changes and tests.~~ A fetch for something already in a payload the palette holds.
2. ~~**Phases join `library`** with the standing documents.~~ Would put a second home under a type that has one.
3. **Leave it.** Still a live option and now the only real question: phases *are* reachable from the Features navigator, the overview strip and `docs/PHASES.md`, so what is missing is finding one **by typing its id**. 34 rows against ~750 is a rounding error in the corpus, and an exact id match scores 1000, so the cost is close to nothing — but it is Edwin's call, and the issue stays open for it.

## Reproduced, 2026-08-14, against the live sidecar

Built the corpus exactly as `buildQuickCorpus` does — the four `QUICK_CORPUS_MODES`, flattened the way `flattenNavItems` flattens them — and typed the ids at it. **874 items**, and:

| typed | result |
|---|---|
| `PHASE-030` | **No matches** |
| `PHASE-011` | **one match: `ISS-0071`** — `issues/ISS-0071-Review-Findings-PHASE-011-012.md`, matched on its *filename* |

The second row is the more interesting failure and was not known when this was filed. Typing a phase id does not always return nothing; sometimes it returns **a note about the phase instead of the phase**, scoring 50 on `rel.includes(q)` so it arrives looking like an answer. An empty result tells you the palette cannot do this. A wrong one does not.

## The head harvest fixes 28 of 34, and the six it misses are the ones that need it most

Measured, not assumed: **28 phase ids are available as navigable group heads** across the four modes the palette already fetches. Six are not, because `_features_groups` emits a group only for a phase that has work grouped under it:

| phase | status |
|---|---|
| PHASE-012 | done |
| PHASE-015 | done |
| PHASE-017 | superseded |
| PHASE-018 | superseded |
| PHASE-019 | superseded |
| PHASE-031 | planned |

**A phase with no group on the Features tree is a phase you cannot browse to either** — so these six are precisely the ones for which typing the id is the only route. And 28 of 34 would have left `test_every_id_bearing_type_is_findable_in_the_palette` **green**, because it asserts *not zero* rather than *all*: the partial this note's own opening paragraph warns about, arriving through the fix for it.

## Decision — both halves, 2026-08-14

1. **`flattenNavItems` harvests a group head that names a note.** The class fix: the head carries `key`, `url` and `status` and the corpus builder never read them, so any future mode that groups by an id-bearing note becomes findable for free rather than becoming the next [[ISS-0142]].
2. **`buildQuickCorpus` gains one `/api/cockpit/stats` pass for phases.** Completeness, for the six with no group. Measured at **1.8 ms**, and the payload already carries all 34 with `rel` — this is the same shape as the two passes that exist for changes and tests, and for the same reason: a type with no nav mode of its own.

Option 1 as originally filed is *not* what this is, and the difference matters: that option proposed a fetch **instead of** a nav home, on the belief that phases had none. This is a fetch **beside** one, for the tail the nav home cannot carry.

`buildQuickCorpus` already dedupes by rel path, so the 28 that arrive twice collapse to one row each.

## What is guarded meanwhile

`test_every_id_bearing_type_is_findable_in_the_palette` measures all types at once and names this gap explicitly, so a **third** instance cannot appear silently the way this one did. That guard is the actual product of [[ISS-0142]]: the bug was found by hand twice, and a type added later would have made it three.

## Fixed — 2026-08-14 ([[CHG-20260814-The-Palette-Finds-Every-Phase]])

Verified end to end against a live sidecar on the built bundle, by rebuilding the corpus the way `buildQuickCorpus` builds it and typing the ids at it:

| typed | before | after |
|---|---|---|
| `PHASE-030` | **No matches** | `PHASE-030` — exact id, score 1000 |
| `PHASE-011` | `ISS-0071` (a note *about* the phase) | `PHASE-011` first, `ISS-0071` second |
| `PHASE-017` *(superseded, no group)* | No matches | `PHASE-017` |
| `PHASE-031` *(planned, no group)* | No matches | `PHASE-031` |

**34 of 34 findable**, from 0. The corpus went from 851 unique rows to 885 — exactly the 34, with the 28 that arrive by both routes collapsing on the existing rel dedupe. *(The pre-fix figure reads 874 in the reproduction above because that counts rows before the dedupe; 851 is what survived it.)*

Both halves landed as decided, and the type went into the group payload rather than being inferred from the key's shape — a second place deciding what a `PHASE-` prefix means is the kind of parallel rule this repo keeps paying for.

**Three guards, each mutation-tested by reintroducing the defect:**

- `flattenNavItems` is asserted to read `group.url`/`group.key`, in the source. **This one exists because of a hole in the other:** `test_every_id_bearing_type_is_findable_in_the_palette` *models* the harvest in Python to measure coverage, so deleting the harvest from the renderer left it green — it would have gone on measuring a corpus the code no longer builds. Deleting the harvest now fails this assertion.
- `buildQuickCorpus` is asserted to fetch `cockpit/stats`, beside the existing assertions for `review-queue` and `cockpit/changes`.
- The reachability guard asserts phases are **complete**, not merely non-zero. Mutated by dropping `rel` from the overview's phases, it reports *"28 of 34 reach the palette"* — the partial that `found > 0` would have called fixed.

`KNOWN_ABSENT` also gained the reverse check I owed it: an exemption must still *be* one, so a type that gains a route can no longer keep a line claiming a defect it does not have. This file carried exactly that for a day — the wrong cause for phases, in the exemption for phases.

## Not a defect: plans

54 `plan` notes are also unreachable by id, and correctly so — `PLAN.md` carries no `id:` field at all. They are reached by path through their feature. Recorded so the next measurement does not re-file them.
