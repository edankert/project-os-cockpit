---
type: "[[task]]"
id: TASK-0274
aliases: ["TASK-0274"]
title: "The right context pane renders as record cards — a head per type with a count, body closed when the type is settled"
status: done
phase: "[[PHASE-022-Completed-Work-Gets-Quieter]]"
owner: user:edwin
created: 2026-08-02
updated: 2026-08-02
source: ["[[FEAT-0057-The-Record-Grammar]]"]
parent: "[[FEAT-0057-The-Record-Grammar]]"
effort: S
depends: ["[[TASK-0271-One-Line-Rows-In-Both-Panes]]", "[[TASK-0272-Status-Said-Once-At-The-Head]]"]
blocks: []
related: ["[[TASK-0269-The-Context-Pane-Stops-Filtering]]"]
tests: ["[[TST-0023-Completed-Work-Ordering]]"]
---

# The context pane becomes record cards

## Definition of Done

- Each type group renders as a card head — `TASKS · 5 · all done` — with the rows in a body that is **closed when every item in it is terminal** and open otherwise.
- Nothing is filtered. [[TASK-0269]]'s rule is untouched and its guards must still pass: `contextGroupRows` still takes no collapse parameter, and a fully-completed group still renders in full **once opened**.
- The length fold stays inside the body, so PHASE-007's 79-item backlinks group is still cut at 12.

## The distinction that has to survive

Closing a body is **not** filtering. [[TASK-0269]] established that this pane describes the note and its completed children are part of what the note *is*; a closed card still says the relationship exists, its type, and how many. A filter said nothing at all — that is the difference, and it is the reason this is allowed where the filter was not.

The guard that enforces it is structural: `contextGroupRows` has no parameter with which to filter, so a disclosure default cannot become one.

## Verification

FEAT-0051 renders four closed cards naming 9 links; opening any card shows every row including the completed ones.
