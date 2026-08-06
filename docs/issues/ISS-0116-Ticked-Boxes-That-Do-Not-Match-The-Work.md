---
type: "[[issue]]"
id: ISS-0116
aliases: ["ISS-0116"]
title: "Five ticked boxes in the fix round describe work that was not done — including the snapshot's own task list, which is now the stale side of the exact drift [[ISS-0112]] was filed about"
status: fixed
phase: ""
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
source: ["review:independent-2026-08-06-round-2"]
severity: low
component: "docs"
related: ["[[ISS-0112-FEAT-0081-Was-Never-Updated-For-Its-Second-Surface]]", "[[ISS-0110-The-Whole-Cold-Reads-Grey-Behaviour-Can-Be-Reverted-With-A-Green-Suite]]", "[[CHG-20260806-Review-Findings-Fixed]]", "[[FEAT-0081-What-A-Session-Costs-To-Keep-Alive]]"]
tests: []
---

# Ticked boxes that do not match the work

## Problem

Each of these is small. They are filed together because they are one failure mode — the box ticked to the shape of the intention rather than the shape of the result — and it is the failure mode the whole [[ISS-0112]] thread is about.

### 1. The snapshot's `tasks:` list for FEAT-0081 was never extended

[[ISS-0112]] was filed because the note and `SNAPSHOT.yaml` disagreed about what FEAT-0081 contained. After the fix they still disagree, with the sides swapped:

| | FEAT-0081 note | `SNAPSHOT.yaml` |
|---|---|---|
| `tasks` | TASK-0343 … **TASK-0353** (11) | TASK-0343 … TASK-0347 (5) |
| `fixes` | ISS-0104 … ISS-0112 | ISS-0104 … ISS-0112 |

`fixes:` was updated in the snapshot; `tasks:` was not. The six new task *entries* exist under `items.tasks` with `parent: FEAT-0081`, so the information is in the file twice and contradicts itself.

The new `PARENT-BACKLINK` gate cannot see this: it walks note frontmatter, and membership in the snapshot is curation `sync-snapshot.py` deliberately leaves alone. So the generalisable half of [[ISS-0112]] closed the note-to-note direction and left the note-to-snapshot direction exactly as it was.

### 2. `PARENT-BACKLINK` does not check the `fixes:` direction

[[ISS-0112]]'s Next Action, ticked:

> - [x] Add a reverse-link check to `validate-docs.sh`: every note with `parent: FEAT-X` appears in FEAT-X's `tasks:`; **every `fixes:` has a matching `parent:`/`related:`**

[[TASK-0353]]'s DoD, ticked:

> - [x] **The validator checks the reverse direction**: a note declaring `parent:` **or `fixes:`** must be declared back by the note it names.

The implemented check walks children with `parent:` and looks up. Nothing walks a feature's `fixes:` and looks down. A feature can name any issue it likes with no obligation on the other end — which is how ISS-0106…ISS-0112 are linked today, and they are fine, but the check ticked is not the check built. [[CHG-20260806-Review-Findings-Fixed]]'s Impact section describes the narrow check accurately, so the two documents disagree.

### 3. TASK-0347's DoD was not corrected

[[ISS-0110]]'s Next Action, ticked:

> - [x] Correct the coverage wording in the CHG and **in TASK-0347's DoD**

`git log` shows [[TASK-0346-Cold-Reads-Grey-And-Actually-Ticks]] and [[TASK-0347-Cold-Sessions-Leave-The-Needs-You-List]] last touched by `165276b`; neither is among `4de65a3`'s files. TASK-0347 still reads "the node suite proves it for the shared `cacheTemperature` decision; the list actually emptying was verified over CDP … not by a suite", which is now **understated in the other direction** — `attentionIds` is guarded at the boundary by two node cases. Nothing there is misleading about coverage any more; it is just no longer true.

### 4. Stale figures the correction pass did not reach

- `src/project_os_cockpit/session_cache.py:484` — "6 of the **17** measured sub-hour re-writes"
- `docs/features/session-economics/plan/PLAN.md:34` — "6 of the **17** sub-hour re-writes"

Both are the retracted denominator; it is 14. Neither was in [[ISS-0111]]'s enumerated list, which is why they survived — the correction was applied to a list rather than to a search.

### 5. Two change notes now carry contradictory follow-up bullets

`CHG-20260806-Session-Cache-Economics.md` lists, three lines apart:

```
- [x] **Independent review is owed** … Not yet run.
- [x] ~~Independent review is owed~~ — run 2026-08-06, returned `changes-requested` …
```

`CHG-20260806-Cold-Sessions-Read-Grey.md` does the same for "The tick has no regression test". Ticking an item by appending a second copy of it leaves the first one asserting the opposite, and the unticked one is what the cockpit's own overview counts.

Related, minor: [[CHG-20260806-Review-Findings-Fixed]]'s coverage line reads "`tests/test_session_cache.py` 19 → 39". That file holds 32; 39 is it plus `test_session_cache_surface.py`'s 7.

## Expected

Each box either untocked or made true. Item 1 matters most — it is the same defect, in the same feature, one round later.

## Actual

Five ticks that would each have been caught by opening the file they name.

## Next Actions
- [x] Add TASK-0348…TASK-0353 to `items.features.FEAT-0081.tasks`
- [x] Untick or implement the `fixes:` direction of `PARENT-BACKLINK`; make the CHG, the issue and the DoD say the same thing
- [x] Update TASK-0347's DoD parenthetical
- [x] Fix the two "6 of the 17" occurrences; prefer `grep` over an enumerated list next time a figure is retracted
- [x] Collapse the duplicated follow-up bullets in both change notes
