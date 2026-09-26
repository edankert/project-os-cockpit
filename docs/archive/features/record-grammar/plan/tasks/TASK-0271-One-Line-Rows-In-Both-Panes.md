---
type: "[[task]]"
id: TASK-0271
aliases: ["TASK-0271"]
title: "Nav and context rows collapse to one line — ID, ellipsised title, chip — at the record column's height"
status: done
phase: "[[PHASE-022-Completed-Work-Gets-Quieter]]"
owner: user:edwin
created: 2026-08-02
updated: 2026-08-02
source: ["[[FEAT-0057-The-Record-Grammar]]"]
parent: "[[FEAT-0057-The-Record-Grammar]]"
effort: M
depends: []
blocks: ["[[TASK-0272-Status-Said-Once-At-The-Head]]"]
related: []
tests: ["[[TST-0023-Completed-Work-Ordering]]"]
---

# One-line rows

## Definition of Done

- A nav row renders `ID · title · chip` on one line, at the record column's height (27px measured, against 60px today).
- The type icon goes: the ID is already type-coloured by `.ov-typed`, so the icon is a second encoding of the same fact in twice the space.
- The `<li>` keeps `data-rel`, `data-id`, `data-type`, `data-status` and the `nav-item` class **unchanged** — the router, `refreshActiveNavRow`, the context menu and the status-flash animation all key off them.
- The **agent chip survives**. A live session touching a note is the one thing on that row that is not derivable from the note, and it is the reason to look at the pane at all.
- Both surfaces.

## Notes

The title stops being a `<p>` on its own line and becomes an ellipsised span. That is the whole 33px: the second line, its margin, and the icon's gutter.

## Verification

Rendered offscreen in the running app and measured, the way the 60/27 figures were obtained in the first place — not asserted from CSS source.
