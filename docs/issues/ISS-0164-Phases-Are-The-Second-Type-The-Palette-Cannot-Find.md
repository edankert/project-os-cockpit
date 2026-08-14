---
type: "[[issue]]"
id: ISS-0164
aliases: ["ISS-0164"]
title: "Phases are the second note type the quick palette cannot find — 34 notes, the same defect [[ISS-0142]] described for releases and claimed was the only one"
status: "open"
phase: "[[PHASE-999-Future]]"
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

## What is guarded meanwhile

`test_every_id_bearing_type_is_findable_in_the_palette` measures all types at once and names this gap explicitly, so a **third** instance cannot appear silently the way this one did. That guard is the actual product of [[ISS-0142]]: the bug was found by hand twice, and a type added later would have made it three.

## Not a defect: plans

54 `plan` notes are also unreachable by id, and correctly so — `PLAN.md` carries no `id:` field at all. They are reached by path through their feature. Recorded so the next measurement does not re-file them.
