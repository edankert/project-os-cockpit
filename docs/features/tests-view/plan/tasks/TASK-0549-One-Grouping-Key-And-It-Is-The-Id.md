---
type: "[[task]]"
id: TASK-0549
aliases: ["TASK-0549"]
title: "Retire `section:`/`ordinal:` — order on `(tier, note_id)`, group on `area` alone"
status: done
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
parent: "[[FEAT-0128-The-Tests-View-Leads-With-The-Work]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# [[ISS-0224]]

## Definition of Done

- [x] `sort_items` keys on `(tier, note_id)` — proved order-identical on all three repos, which is the measurement the issue rests on.
- [x] `view_payload` and `_acceptance_tier_groups` group on `area` alone.
- [x] `Item.number` is the note id; the `.0` fallback goes with the fields that caused it.
- [x] The fields leave `test.md`, `SCHEMAS.md` and the validator — **upstream first**, and refused **only in a repo that keeps ledgers**.
- [x] `acceptance.parse` still derives them for the file shape, and `suite_at` still reads the twelve pre-migration tags. This is removal from the **note schema**, not from the parser.

## Done 2026-08-19

Order is `(tier, note_id)`; `Item.number` **is** the id; grouping is `area` alone. The fields left `test.md`, `SCHEMAS.md` (here and upstream) and are refused by `LEDGER-FIELD` — only in a repo that keeps ledgers, so the eight unmigrated repos are untouched. 34 notes stripped here.

**A file-shape row keeps its position**, because it has no note and that is the only address it has. Permanent branch: twelve historical tags hold that shape and a tag is immutable.

`test_the_view_holds_every_check_in_suite_order` was asserting the *document's* order. It asserts `(tier, id)` now, and the comment says why the order did not move — only the thing expressing it did.

**A guard was added that this task needed and did not have.** Wiring the tasks into `FEAT-0128` truncated its `tasks:` list, producing a note whose frontmatter would not parse — the **second** time in one session, after `TASK-0521`'s unescaped quotes, and both went past a green validator. `NOTE-FRONTMATTER` now catches it, using a real YAML parse rather than this script's deliberate subset, which read `title: "Retire "walk" from it"` without complaint. It closes [[ISS-0214]]'s second done-when.