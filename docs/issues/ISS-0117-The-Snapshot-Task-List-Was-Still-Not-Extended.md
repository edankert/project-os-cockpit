---
type: "[[issue]]"
id: ISS-0117
aliases: ["ISS-0117"]
title: "`items.features.FEAT-0081.tasks` still lists five of thirteen tasks — the finding [[ISS-0116]] filed, ticked as fixed and asserted as corrected in the change note, in a commit that edits the very file"
status: fixed
phase: ""
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
source: ["review:independent-2026-08-06-round-3"]
severity: medium
component: "docs"
related: ["[[ISS-0116-Ticked-Boxes-That-Do-Not-Match-The-Work]]", "[[ISS-0112-FEAT-0081-Was-Never-Updated-For-Its-Second-Surface]]", "[[FEAT-0081-What-A-Session-Costs-To-Keep-Alive]]", "[[CHG-20260806-Round-Two-Findings-Fixed]]"]
tests: []
---

# The snapshot's task list for FEAT-0081 was still not extended

## Problem

[[ISS-0116]] finding 1 was that `SNAPSHOT.yaml`'s `items.features.FEAT-0081.tasks` listed five tasks while the note listed eleven. It is unchanged at `HEAD` (`907fe14`):

```
SNAPSHOT.yaml:61   tasks: [TASK-0343, TASK-0344, TASK-0345, TASK-0346, TASK-0347]
```

Against that, at the same commit:

| | count |
|---|---:|
| `tasks:` in FEAT-0081's frontmatter | 13 (TASK-0343 … TASK-0355) |
| files in `docs/features/session-economics/plan/tasks/` | 13 |
| `items.tasks` entries carrying `parent: FEAT-0081` | 13 |
| `items.features.FEAT-0081.tasks` | **5** |

The sibling key was updated in the same commit — `fixes:` grew to ISS-0104 … ISS-0116. `tasks:` did not.

## Why this is not a phrasing problem

It is ticked as done and asserted as done, in three places:

- [[ISS-0116]] Next Actions: `- [x] Add TASK-0348…TASK-0353 to items.features.FEAT-0081.tasks`
- [[TASK-0355-The-Record-Stops-Overclaiming]] DoD: `- [x] items.features.FEAT-0081.tasks lists all eleven tasks and every fixed issue`
- [[CHG-20260806-Round-Two-Findings-Fixed]], Summary: "Corrected, along with `items.features.FEAT-0081.tasks` (5 of 11 listed — ISS-0112's drift with the sides swapped)"

This is the fourth consecutive appearance of the [[ISS-0112]] drift, and the second time it has been recorded as repaired without being repaired. `SNAPSHOT.yaml` is where a session that has read nothing else learns what FEAT-0081 contains; closing the feature on this entry closes it with eight of its thirteen tasks invisible from the canonical file — which is the harm [[ISS-0112]] was filed to describe.

## Why the round's own corrective could not catch it

[[CHG-20260806-Round-Two-Findings-Fixed]] names the mechanical rule it installed:

> before ticking a box that names a file, confirm the file is in the diff.

`SNAPSHOT.yaml` **is** in the diff — 56 changed lines, including the corrected prose notes and the extended `fixes:`. File presence is not the property being claimed; the claim is about a specific key's contents. The rule as written passes this case, so the corrective is weaker than the defect it was written for.

`PARENT-BACKLINK` cannot see it either, and this was verified rather than assumed: deleting `TASK-0354` from FEAT-0081's *note* produces `ERROR [PARENT-BACKLINK] TASK-0354 declares parent: FEAT-0081, but FEAT-0081 does not name it in tasks:`, while the snapshot's five-item list produces nothing. The gate walks note frontmatter only, which the notes already say.

## Repro

```
python3 -c "import yaml;d=yaml.safe_load(open('SNAPSHOT.yaml'));print(d['items']['features']['FEAT-0081']['tasks'])"
# ['TASK-0343', 'TASK-0344', 'TASK-0345', 'TASK-0346', 'TASK-0347']
ls docs/features/session-economics/plan/tasks | wc -l          # 13
```

## Expected

`items.features.FEAT-0081.tasks` carries all thirteen, and the boxes that claim it does are true — or, if the snapshot's membership is deliberately a subset, that is stated once and the boxes stop claiming completeness.

## Actual

Five of thirteen, ticked as thirteen, in the round whose subject was ticked boxes that do not match the work.

## Next Actions
- [x] Extend `items.features.FEAT-0081.tasks` to TASK-0343 … TASK-0355
- [x] Correct or untick the three places that claim it was already done
- [x] Decide whether the corrective is "confirm the file is in the diff" or "confirm the **claim** is in the diff" — the first does not catch this
