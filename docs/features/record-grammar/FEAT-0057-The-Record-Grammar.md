---
type: "[[feature]]"
id: FEAT-0057
aliases: ["FEAT-0057"]
title: "Both panes adopt the record column's grammar — one-line rows, status said once at the head, and finished groups rolled up behind a divider"
status: done
phase: "[[PHASE-022-Completed-Work-Gets-Quieter]]"
owner: user:edwin
created: 2026-08-02
updated: 2026-08-02
source: ["Edwin 2026-08-02, on the FEAT-0056 result: 'it still shows too many done items and too much info, not concise enough. I kinda like the very minimalist new way to present the ADR, TSTs etc FEAT, ISS etc as they are shown in the project overview context, maybe we should move to use that kinda look and feel instead as well for both the left-pane and right pane'"]
goal: "Give the navigator and the context pane the density the record column already has, so that folding completed work actually reads as quieter instead of merely shorter."
requirements: []
tasks:
  - "[[TASK-0271-One-Line-Rows-In-Both-Panes]]"
  - "[[TASK-0272-Status-Said-Once-At-The-Head]]"
  - "[[TASK-0273-Finished-Groups-Roll-Up]]"
  - "[[TASK-0274-The-Context-Pane-Becomes-Record-Cards]]"
release: ""
related: ["[[FEAT-0056-Completed-Work-Ordering]]", "[[FEAT-0043-Overview-Rework]]", "[[DES-0004-Attention-In-The-Squares]]"]

---

# The record grammar

## Where this came from

[[FEAT-0056]] changed **what** the navigator shows. It did not change **how densely**, and at this density its own fix is hard to see.

Measured in the running app, same note, same text:

| | row | group head | one group of 1 |
|---|---|---|---|
| nav / context pane | **60px** | **53px** | 114px |
| record column | **27px** | **15px** | ~45px |

The nav row is 2.2× taller because it puts ID and chip on one line and the title on a second, and carries a type icon that repeats what the type-coloured ID already says.

More importantly: the features view renders **eighteen 53px group headers** whether or not anything in them is live. After all of FEAT-0056's folding, **the headers became the noise**.

## What actually makes the record column concise

Four moves, and only one of them is "smaller rows". FEAT-0056 implemented only the fourth, and only *within* a group:

1. **One line** — `FEAT-0056  Open work sorts first…  done`. No icon, no wrap, title ellipsised.
2. **Status said once, at the head** — `DECISIONS · 7 · all accepted`. The ADR card does not print "accepted" seven times. At 99% completion nearly every group is uniform, so the per-row chip is one word repeated — 261 times in the tasks view.
3. **Closed by default, with a count** — a settled group is *one line*, not a header plus a fold row.
4. **A cut, then `N older`.**

## The shape

Edwin chose the most concise option on both panes.

**Left pane** — live groups open and compact; everything finished behind one divider:

```
FEATURES
▾ PHASE-022 · Completed work gets quieter    1
     FEAT-0056  Open work sorts first, long l…
▸ PHASE-999 · Future / Unphased              1
──────────────────────────────────────────────
▸ 16 finished phases · 53 features
```

**Right pane** — the record column's own markup, settled types closed:

```
CONTEXT · FEAT-0051
▸ TASKS        5 · all done
▸ FEATURES     2 · all done
▸ PHASES       1 · all done
▸ PLAN         1 · all done
```

Nothing is removed. The roll-up expands to the one-line-per-group view; each group expands to its rows.

## Scope

[[TASK-0271]] the row, [[TASK-0272]] the head, [[TASK-0273]] the roll-up, [[TASK-0274]] the context cards.

## Out of Scope

- **The overview itself.** It is the model being copied, not a thing to change.
- **Ordering and the collapse rule.** [[FEAT-0056]] settled both; this is presentation over the same data, and its guards must keep passing untouched.

## The thing most likely to break

**A note inside a rolled-up group must still be reachable and still highlight.** `refreshActiveNavRow` keys off `li.dataset.rel`, and a row inside a closed `<details>` is in the DOM but invisible — so navigating to a finished feature would highlight a row nobody can see. Any group containing the active note has to open itself.
