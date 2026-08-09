---
type: "[[task]]"
id: TASK-0367
aliases: ["TASK-0367"]
title: "Task children sort by status and fold when finished, so a 48-task feature stays readable"
status: backlog
phase: "[[PHASE-022-Completed-Work-Gets-Quieter]]"
owner: user:edwin
created: 2026-08-09
updated: 2026-08-09
source: ["[[FEAT-0085-The-Navigator-Shows-The-Structure-The-Record-Has]]"]
parent: "[[FEAT-0085-The-Navigator-Shows-The-Structure-The-Record-Has]]"
effort: M
due: ""
depends: ["[[TASK-0366-Tasks-Join-Their-Feature]]"]
blocks: []
related: ["[[FEAT-0056-Completed-Work-Ordering]]", "[[FEAT-0058-One-Shape-Per-Navigator]]"]
tests: []
---

# Task children sort by status and fold

## Definition of Done
- [ ] Task children sort open-first by the comparator this phase already established — not a second one
- [ ] Finished tasks fold behind the same `✓ N` / `Completed · N` affordance the navigators already use
- [ ] The 48-task feature and the median 3-task feature both read well; checked against the real corpus, not a fixture
- [ ] Neither renderer declares its own completed-status set

## Steps
- [ ] Reuse `open_first_key` — the same comparator features already sort by ([[TASK-0267]] made it one comparator on purpose)
- [ ] Apply the existing fold at child level; check the indent rule from [[ISS-0093]] still holds at the new depth, since a parent must never indent further than its children
- [ ] Render the depth in both `renderer.ts` and `cockpit.js`
- [ ] Look at the real tree at both extremes before calling it done

## Notes
Two traps this phase has already fallen into, both applicable here:

**One comparator.** [[TASK-0267]] collapsed open-before-done to a single comparator precisely because a second one drifts. Task children must use it rather than sorting by a local status list.

**Compounding indents.** [[ISS-0093]]: no single indent value was wrong, but the band's 6, the group's 2 and the head's 8 compounded until a phase id sat 2px right of its own children. This adds a level, so it is the change most likely to reproduce that. The fix that held was that the *body* carries the indent, not the group.

Median 3 is the case to optimise for; 48 is the case that must not break.
