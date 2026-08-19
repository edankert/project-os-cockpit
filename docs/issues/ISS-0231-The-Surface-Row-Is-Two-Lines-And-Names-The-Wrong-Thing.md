---
type: "[[issue]]"
id: ISS-0231
aliases: ["ISS-0231"]
title: "A surface row stacks its bar on a second line and shows the area string where a regression's issue title belongs — the phase row's layout was copied, not its shape"
status: fixed
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
severity: high
component: cockpit-desktop
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[ISS-0222-The-Left-Pane-Groups-By-Tier-And-Nothing-Else]]", "[[ISS-0230-The-Browser-Cockpit-Has-No-Surface-Row]]", "[[DES-0012-Tests-In-Two-Flows]]"]
---

# One line, and the right title

Edwin, 2026-08-19, on the third attempt: *"Wow, that is really bad."*

`navItemSurface` was built from `buildPhaseRow` and took its **vertical stack** — title on one line, `.ov-phase-under` on the next. What was asked for was the phase row's **elements, on one line**.

## What it should be

**Feature tests** — `[open/close] [surface title] [progress bar] [%]`, one line.

**Regression tests** — `[open/close] [issue-id] [issue title] [progress bar] [%]`, one line, and **the issue's own title** rather than the `area:` string. Those are different things: a Tier 2 `area:` is free text somebody typed, and the issue has a title of its own that the index can resolve.

**Expanded** — the checks as now, with their state **right-aligned**.

## Why it keeps going wrong

Three attempts, one cause: each was built from an interpretation of the description rather than from the named model, and each was verified against the payload rather than the screen. The bar has now been put in three places, none of them the one asked for.

## Done when

- [x] A feature-test row is one line: handle, title, bar, percentage.
- [x] A regression row is one line and carries the issue's id **and its real title**.
- [x] Expanded checks right-align their state.
- [x] The same in both front doors ([[ISS-0230]]).

## Fixed 2026-08-19
