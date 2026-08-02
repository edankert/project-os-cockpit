---
type: "[[plan]]"
title: "Plan — the record grammar"
status: done
owner: user:edwin
created: 2026-08-02
updated: 2026-08-02
parent: "[[FEAT-0057-The-Record-Grammar]]"
---

# Plan

Row, then head, then roll-up — each one visible on its own, and each one strictly smaller than the last in risk.

1. **[[TASK-0271]]** — the one-line row. Pure presentation; the `li` keeps every data attribute the router, the active-row highlight, the context menu and the status-flash animation key off.
2. **[[TASK-0272]]** — the group head carries the count and, when the group is status-uniform, the status; the per-row chip drops in that case. Depends on 0271 for the row it edits.
3. **[[TASK-0273]]** — the roll-up divider, and the auto-open rule that keeps the active note reachable inside it. The only task with real behaviour in it.
4. **[[TASK-0274]]** — the context pane becomes record cards. Independent of 0273; shares the row and head from 0271/0272.

Both surfaces throughout — mode 1 and mode 3 drifted twice during [[FEAT-0056]] and were caught by review both times. Guards go in with each task, not after.
