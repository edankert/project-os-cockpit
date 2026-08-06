---
type: "[[issue]]"
id: ISS-0118
aliases: ["ISS-0118"]
title: "Three ticked boxes in the round-two fix name artefacts the commit never touched — the duplicated follow-up in the second change note, the stale `focus`, and [[TASK-0351]]'s DoD"
status: fixed
phase: ""
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
source: ["review:independent-2026-08-06-round-3"]
severity: low
component: "docs"
related: ["[[ISS-0116-Ticked-Boxes-That-Do-Not-Match-The-Work]]", "[[ISS-0113-SNAPSHOT-Still-Quotes-The-Retracted-Figures]]", "[[ISS-0115-ISS-0110s-Repro-Still-Reproduces]]", "[[CHG-20260806-Round-Two-Findings-Fixed]]"]
tests: []
---

# Three more ticked boxes that name files the commit did not touch

## Problem

Each is small and none affects behaviour. They are filed together because they are one failure mode, they are the *same* failure mode [[ISS-0116]] filed, and they are inside the fix for it. Every one is decided by opening the file the box names.

### 1. Only one of the two change notes had its duplicated follow-up collapsed

`docs/changes/CHG-20260806-Cold-Sessions-Read-Grey.md:68-69` still carries the contradictory pair verbatim:

```
- [x] ~~The tick has no regression test~~ — narrower than stated … guarded by the node suite and verified by mutation.
- [x] **The tick has no regression test.** Proving it needs a DOM …
```

`git log -- docs/changes/CHG-20260806-Cold-Sessions-Read-Grey.md` last shows `4de65a3`; the file is not among `907fe14`'s staged paths. `CHG-20260806-Session-Cache-Economics.md` *was* fixed in that commit, so exactly half the work was done.

Ticked as whole in two places:

- [[TASK-0355-The-Record-Stops-Overclaiming]] DoD: `- [x] … the duplicated follow-up lines in both earlier change notes resolved to one each.`
- [[ISS-0116]] Next Actions: `- [x] Collapse the duplicated follow-up bullets in both change notes`

The consequence [[ISS-0116]] itself named still holds: the unticked copy is what the cockpit's own overview counts, so this note still reports an open follow-up that the line above it says is closed.

### 2. `focus` still points at two terminal items

[[ISS-0113]] Next Actions: `- [x] Move focus onto the work actually in flight`.

`SNAPSHOT.yaml:48-51` is unchanged: `focus.task: "TASK-0343"` (`status: done`) and `focus.issue: "ISS-0104"` (`status: fixed`). The `focus.note` beside them was rewritten in the same commit, so the block was edited and these two keys were not.

Lower stakes than the rest — [[ISS-0113]] said so when it filed it — but the box says otherwise.

### 3. TASK-0351's DoD still claims coverage the round re-verified it does not have

[[ISS-0115]] Next Actions: `- [x] Correct the sentence in [[CHG-20260806-Review-Findings-Fixed]] and the ticked DoD in [[TASK-0351]]`.

The CHG sentence was corrected, and correctly — it now says deleting the DOM adapters leaves the suite green. [[TASK-0351-Pure-Decisions-For-The-Rail-And-The-Badge]] is not among the commit's files, and its DoD still reads:

> - [x] The three call sites become one-line adapters, **so reverting the behaviour means deleting a tested function rather than an untested branch.**

The first clause is now true — `tickTemperatures` calls `railKey`, which is the good half of this round. The clause after "so" is the claim [[ISS-0115]] refuted and [[CHG-20260806-Round-Two-Findings-Fixed]] concedes under "What is still not fixed". Two documents in the same feature now say opposite things about the same suite.

Related, in the same file and unticked-worthy on the same grounds: `- [x] Verified by mutation … Recorded in the task.` The task's Notes section records no mutations.

## Expected

Each box either made true or unticked. All three are one-line edits.

## Actual

Three ticks that would each have been settled by opening the file they name — which is the corrective [[CHG-20260806-Round-Two-Findings-Fixed]] says it applied to every ticked box in this feature's tasks.

## Next Actions
- [x] Collapse the duplicated follow-up in `CHG-20260806-Cold-Sessions-Read-Grey.md`, or untick the box that says both were done
- [x] Move `focus.task` / `focus.issue`, or untick
- [x] Narrow [[TASK-0351]]'s second DoD clause to what the suite covers, and record its mutation results or drop the claim that they are recorded
