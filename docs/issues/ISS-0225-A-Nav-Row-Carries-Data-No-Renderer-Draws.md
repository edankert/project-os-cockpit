---
type: "[[issue]]"
id: ISS-0225
aliases: ["ISS-0225"]
title: "The surface percentage is computed, sent and discarded — `buildNavRow` documents that `subtitle` is never rendered, and nothing fails when a payload carries a field no renderer draws"
status: fixed
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
severity: high
component: cockpit-desktop
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[ISS-0222-The-Left-Pane-Groups-By-Tier-And-Nothing-Else]]", "[[ISS-0226-A-Surface-Wears-A-Test-Status]]", "[[TASK-0550-The-Nav-Groups-By-Surface]]"]
---

# Sent, and thrown away

Edwin, 2026-08-19: *"why does the left hand pane still not show the completion bar for each of these sections/areas."*

**Because it never rendered.** [[TASK-0550]] put the surface's progress in the nav row's `subtitle`, and `buildNavRow` says in its own docstring:

> *"`item.subtitle` is deliberately NOT rendered. It is the second line, and the server sends one for every feature (`goal`), design and risk … The left pane is a selection list."*

So `82% · 27/33` is computed per surface, serialised, sent over the wire, and dropped on the floor. Every test of it passes, because every test asserts the **payload**.

## The class, which matters more than the instance

**Nothing anywhere fails when the server sends a field no renderer draws.** That is what let this ship: the work was verified against the payload and never against the screen, and the payload was correct.

## Suggested fix

1. **Render the bar, and make it a sliver.** `.ov-phase-under` already exists — 2px, and it is the exact instrument Edwin is comparing to (*"the same as we do for phases"*). A one-line row has room for an underline; it does not have room for a segmented block.
2. **The counts go in text the row actually draws.** `27/33` belongs beside the surface name, not in a field the renderer discards.
3. **A guard for the class.** A test that walks the nav payload's item keys against the set `buildNavRow` reads, and fails on a key nothing draws. It would have caught this before the restart, and it catches the next one — the failure mode is silent by construction, so only a mechanical check sees it.

## Done when

- [x] A surface row draws its progress.
- [x] A payload field no renderer reads is a test failure, not a shrug.
