---
type: "[[task]]"
id: TASK-0273
aliases: ["TASK-0273"]
title: "Finished groups roll up behind one divider, and any group holding the active note opens itself"
status: done
phase: "[[PHASE-022-Completed-Work-Gets-Quieter]]"
owner: user:edwin
created: 2026-08-02
updated: 2026-08-02
source: ["Edwin 2026-08-02, choosing the most concise of three densities offered"]
parent: "[[FEAT-0057-The-Record-Grammar]]"
effort: M
depends: ["[[TASK-0271-One-Line-Rows-In-Both-Panes]]", "[[TASK-0272-Status-Said-Once-At-The-Head]]"]
blocks: []
related: ["[[TASK-0268-Groups-With-Open-Work-Sort-First]]"]
tests: ["[[TST-0023-Completed-Work-Ordering]]"]
---

# Finished groups roll up

## Definition of Done

- Groups with no open work render below a divider as **one** expandable line: `▸ 16 finished phases · 53 features`.
- Expanding it yields the one-line-per-group view; expanding a group yields its rows. **Two clicks reach any note**, and nothing is unreachable.
- The counts are always shown — a roll-up that does not say how much it rolled up is indistinguishable from an empty pane, which is the failure [[FEAT-0056]] exists to have fixed.
- **A group containing the active note opens itself**, roll-up included. See the risk below.
- Both surfaces.

## The failure this must not have

`refreshActiveNavRow` sets `is-active` on the `li` whose `data-rel` matches. A row inside a closed `<details>` is in the DOM and matches — so it would highlight where nobody can see it, and the pane would show no selection at all while claiming one.

Navigating to a finished note is not the rare case here: 99% of the corpus is finished. **This is the normal path**, not an edge.

## Verification

Navigate to a note inside the roll-up; the roll-up, its group, and the row are all open and the row carries `is-active`. Asserted against the live DOM, not against the model.
