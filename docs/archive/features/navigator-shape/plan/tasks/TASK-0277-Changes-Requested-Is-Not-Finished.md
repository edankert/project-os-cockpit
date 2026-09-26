---
type: "[[task]]"
id: TASK-0277
aliases: ["TASK-0277"]
title: "The review desk promotes changes-requested into a live section and collapses the rest into cards per verdict"
status: done
phase: "[[PHASE-022-Completed-Work-Gets-Quieter]]"
owner: user:edwin
created: 2026-08-02
updated: 2026-08-02
source: ["Edwin 2026-08-02: 'The Review section does not have a completed section at the moment, a little of an odd one out, please suggest how to handle.'"]
parent: "[[FEAT-0058-One-Shape-Per-Navigator]]"
effort: M
depends: []
blocks: []
related: ["[[ISS-0069-Review-Verdict-Vocabulary-Is-Unguarded]]"]
tests: ["[[TST-0023-Completed-Work-Ordering]]"]
---

# changes-requested is not finished

## Definition of Done

- A `Changes requested · N` section sits with the live work, above the divider.
- `Completed · N` holds one collapsed card per remaining verdict — `approved · 70`, `accepted · 2` — each with its count.
- The `N older` disclosure goes: the cards are what it was approximating.

## Why

`Reviewed · 82` already **was** review's completed section; it only lacked the shape. But **10 of the 82 are `changes-requested`** — a reviewer asked for work and nothing records it having happened.

Filing those under "reviewed" is the same error the old Hide-completed switch made: **a terminal-looking label on something still owed.** The whole phase exists because that error is expensive.

## Notes

Verdict counts measured 2026-08-02: `approved` 70, `changes-requested` 10, `accepted` 2. That `accepted` and `approved` coexist is [[ISS-0069]]'s problem, not this task's — both are read as finished here, and neither is reconciled.

## Verification

The desk shows the 10 changes-requested notes without expanding anything, and 72 behind two cards.
