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

**1. One item, two rows.** `_needs_you_group` is prepended to every view not in `_VIEWS_THAT_ALREADY_GATHER`, and `publication` was not in that set. But the view leads with the ladder and gathers everything it owes into rungs — so `your-trainer`'s single unpushed commit appeared under `Needs you` **and** under `To push · 1`, on one screen.

That is [[ISS-0068]]'s failure. [[ADR-0025]] permits an owed row to appear twice, but as a **shortcut from a view that does not otherwise show it** — *"a shortcut list, not a second home"*. A view that already gathers has no shortcut to offer, only a duplicate.

**2. Rows with no destination.** A reachable rung with nothing at it still renders — that IS the answer, *"nothing to push"* — but its placeholder row carried `url: None`, as did the gate's *nothing blocking* row. A row that does not respond to a click reads as a **broken** row rather than an empty one.

Measured on `your-trainer`: one dead row of 77.

## Fixed 2026-08-16

`publication` joins `_VIEWS_THAT_ALREADY_GATHER`; placeholder rows point at `~history` and at the suite respectively. Two guards in `TST-0027`, and a sweep of every mode in every repo found no other dead row in this view.

## Found while sweeping, not fixed here

`yourtrainer-mcp`'s Intent view has **five** dead rows — standing documents that do not exist, so there is nothing to open. Defensible and pre-existing: the row is reporting an absence. It is arguably a *Create* affordance rather than a link, which is a question for the standing-document surface and not for this issue.

## Also corrected

I told Edwin the Publication button was ninth in the top bar. It is **sixth** — I counted `NAV_MODES`, which carries retired ids (`tasks`, `review`, `active`, `recent`) that render no button.
