---
type: "[[issue]]"
id: ISS-0228
aliases: ["ISS-0228"]
title: "The generated page shows the `TST-*` id at both ends of a row, and neither is selectable — `number` and `id` used to differ and ISS-0224 made them identical"
status: open
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
severity: low
component: cockpit-desktop
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[ISS-0224-The-Positional-Address-Outlived-The-Document]]", "[[TASK-0549-One-Grouping-Key-And-It-Is-The-Id]]"]
---

# One id, drawn twice

Edwin, 2026-08-19: *"why does the generated acceptance test page show the TST identifier at the start and the end of the tst, just have this at the start and make this tst identifier selectable."*

`buildCheckRow` draws `item.number` in `.checks-row-number` at the start, and `item.id` on the `.checks-row-open` button at the end.

**They were different things until this morning.** `number` was the document position — `1.6.150` — and `id` was `TST-0123`; a row showed where the check *was* and what it *is*. [[ISS-0224]] made `number` return the id, and the two collapsed into one value rendered twice.

That is the expected shape of this kind of change and the reason to look at the screen after making it: nothing failed, because both fields were correct.

## Suggested fix

1. **The end button loses its label.** It is an *open* affordance, so it says `open` or carries an icon; the id belongs where a reader looks first.
2. **The start id becomes selectable** — `user-select: text` on `.checks-row-number`, and a `title` naming what it is. It is the value somebody types into the palette or pastes into a note, and today it cannot be copied without opening the check.
3. **While there: the row's area suffix still reads `item.section ? section + area : area`.** `section` is gone from every migrated note, so the ternary is dead in this repo and live in the two that have not migrated. It goes with the fleet migration, not before.

## Done when

- [ ] The id appears once per row.
- [ ] It is selectable and says what it is.
