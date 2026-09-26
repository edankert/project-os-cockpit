---
type: "[[change]]"
id: CHG-20260802-Completed-Work-Collapses
title: "Hide-completed became collapse-completed: nothing is removed by status any more, and the context pane never filters at all"
status: merged
reviewed_by: model:claude-opus-5
review_date: 2026-08-02
review_verdict: changes-requested
date: 2026-08-02
owner: user:edwin
component: [server, static, desktop-renderer]
related: ["[[PHASE-022-Completed-Work-Gets-Quieter]]", "[[FEAT-0056-Completed-Work-Ordering]]", "[[ISS-0082-Phantom-Phase-Group-From-The-016-Merge]]"]
---

# Completed work collapses instead of disappearing

## What changed for anyone using the cockpit

The eye toggle is now **Collapse completed**, and that is what it does. Before — with 99% of this repo's lifecycle notes terminal — turning it on removed 17 of 18 feature groups, all 4 issue severity buckets, and left 5 task rows of 270. It emptied the right-hand context pane of any finished note entirely. It now folds each group at its first completed item and shows a `… N more` row you can click. **No group can vanish**, and the pane that describes a note never filters at all.

Open work also sorts first everywhere state is not already the grouping axis: within severity buckets, within phase groups, and within a feature's nested requirements. Phase groups themselves band into **in flight, upcoming, finished**, so the phase being worked leads the features navigator and the finished ones keep their chronology below it.

Long groups fold on **length** as well, at 12 rows, independently of the switch — so the 261-row `Done` bucket is short whether the switch is on or not. The same limit applies in the context pane, where 11 of 3192 groups exceed it and the largest is 79.

## Behaviour, before and after (switch on)

A *row* is one item row, plus the group's `… N more` row where it has one.

| view | groups / items | before | after |
|---|---|---|---|
| Tasks | 5 / 270 | 2 groups, 5 rows | **5 groups, 8 rows** |
| Features | 18 / 56 | 1 group, 1 row | **18 groups, 18 rows** |
| Issues | 7 / 86 | 3 groups, 4 rows | **7 groups, 8 rows** |
| Context, FEAT-0051 | 4 / 9 | **0 rows** | **9 rows** |
| Context, ISS-0080 | 4 / 5 | **0 rows** | **5 rows** |

## Paths

- `src/project_os_cockpit/cockpit.py` — `open_first_key`, `_open_first`, `_group_is_settled`, `_settled_last`; `_phase_target` now keys on the canonical `PHASE-####`
- `src/project_os_cockpit/static/cockpit.js` — `isHidden` deleted; `openFirst` / `foldGroup` / `appendMoreRow` added
- `desktop/src/renderer/completed-work.ts` — **new**, the pure logic
- `desktop/src/renderer/renderer.ts` — `isItemHidden` deleted; `NAV_GROUP_FOLD_LIMIT` / `CONTEXT_GROUP_FOLD_LIMIT`; the context pane stops reading the switch; nested children order open-first
- `desktop/src/renderer/renderer.css`, `src/project_os_cockpit/static/cockpit.css` — the `… N more` row

## Also fixed

[[ISS-0082]] — a phase rename during the ISS-0077 merge forked PHASE-016 into a phantom group, because `_phase_target` keyed on the whole slug while the overview's `_phase_id_of` extracted the ID. Both now key on the ID, and a guard fails if any `phase:` link points at a note that does not exist.

## Reviewed

Independent review returned `changes-requested` with ten findings; all ten were addressed before this note was written. The largest: the context pane's length fold was documented but not built, a two-band phase sort put the backlog pen permanently above the phase in flight, and five guards did not fail under mutation. The verdict and the findings are recorded in [[FEAT-0056]].

## Restart required

Mode 3 is a built bundle. The change is live after the desktop app restarts.
