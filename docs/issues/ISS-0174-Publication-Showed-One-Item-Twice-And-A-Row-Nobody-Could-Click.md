---
type: "[[issue]]"
id: ISS-0174
aliases: ["ISS-0174"]
title: "The Publication view showed one item twice and carried a row nobody could click — a Needs-you group over a view that already gathers, and placeholder rows with no destination"
status: "fixed"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
source: ["Edwin 2026-08-16, opening the view: 'That is a strange place for it, why in the needs you section, also not all the left-pane items are selectable, please review?'"]
severity: medium
component: cockpit-server
parent: ""
related: ["[[FEAT-0102-Publication-Becomes-A-View]]", "[[ADR-0025-An-Owed-Row-May-Appear-Twice]]", "[[ISS-0068]]"]
tests: ["[[TST-0027-The-Ladder-Is-Non-Empty-In-Every-Repo]]"]
---

# The Publication view showed one item twice, and a row nobody could click

## Two defects, both from use

**1. ~~One item, two rows.~~ WRONG — reversed the same day.** I read *"why in the needs you section"* as an objection to the group and removed it. Edwin meant the **controls** in it, and said so plainly when I asked: *"I don't mind the needs you section, it makes sense to have all the publication completion tasks to be in the needs you section instead of below."*

He is right, and [[ADR-0025]] says so: *"a shortcut list, not a second home — the rows also stay in their structural place, marked."* Publication's rungs are a **ladder**, a record of how far work has travelled, not a gathering of obligations. The ladder is the structural place; `Needs you` is the shortcut. Removing it made the reader hunt the ladder for the two rows that could be acted on.

Restored, and the guard I wrote for the wrong reading is **deleted** rather than weakened — two guards asserting opposite things is worse than either.

**2. Rows with no destination.** A reachable rung with nothing at it still renders — that IS the answer, *"nothing to push"* — but its placeholder row carried `url: None`, as did the gate's *nothing blocking* row. A row that does not respond to a click reads as a **broken** row rather than an empty one.

Measured on `your-trainer`: one dead row of 77.

## Fixed 2026-08-16

`publication` joins `_VIEWS_THAT_ALREADY_GATHER`; placeholder rows point at `~history` and at the suite respectively. Two guards in `TST-0027`, and a sweep of every mode in every repo found no other dead row in this view.

## The second round, same day

Edwin, on the result: *"I don't mind the needs you section … that walk button looks totally out of place there, also the other views hide completed items, so you can only see the next/current items to work on."*

Three more, all correct:

- **The verb had nowhere to live.** Every owed row has named a verb since the registry shipped and **no surface has ever drawn one**, so an action always had to be found somewhere else — which is how `Walk` ended up stranded on a group header. `NavItem` now carries `owed_verb` and an optional `action` route, and the row draws it. `Prepare release…` moved to the rung whose subject is the release list.
- **The ladder never folded.** A ladder is mostly behind you: the releases already out, and the commits the agent makes at close-out. Those rungs now open shut, so the view opens on what is next. Both stay one click away through their header and count. A tag row also carried an empty status, which made the whole `Released` rung read as open work.
- **`Committed · 42` counted UNCOMMITTED notes** — the label said the opposite of the number beside it. It reads `To commit · 42`.

## Found while sweeping, not fixed here

`yourtrainer-mcp`'s Intent view has **five** dead rows — standing documents that do not exist, so there is nothing to open. Defensible and pre-existing: the row is reporting an absence. It is arguably a *Create* affordance rather than a link, which is a question for the standing-document surface and not for this issue.

## Also corrected

I told Edwin the Publication button was ninth in the top bar. It is **sixth** — I counted `NAV_MODES`, which carries retired ids (`tasks`, `review`, `active`, `recent`) that render no button.
