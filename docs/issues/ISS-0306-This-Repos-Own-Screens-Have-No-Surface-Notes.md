---
type: "[[issue]]"
id: ISS-0306
aliases: ["ISS-0306"]
title: "This repo keeps one surface note for fourteen screens, so a change note here cannot name the screen it altered and the walk's own survey has nothing to show"
status: triage
phase: "[[PHASE-999-Future]]"
owner: user:edwin
created: 2026-09-14
updated: 2026-09-14
source: ["Found writing [[CHG-20260914-The-Walk-Page-Reads-As-A-Script]]: its Impact section could name no screen id."]
severity: medium
component: docs
parent: ""
related: ["[[FEAT-0130-Surfaces-Are-A-First-Class-Type]]", "[[TASK-0625-The-Checks-Page-Groups-By-Screen]]", "[[CHG-20260914-The-Walk-Page-Reads-As-A-Script]]", "[[ISS-0250-A-Surface-Rename-Silently-Orphans-Its-Checks]]"]
tests: []
tags: [issue, surfaces, walk]
---

# This repo's own screens have no surface notes

## Problem

`docs/surfaces/` holds exactly one note, `SUR-0001-The-Tests-View`. The cockpit has roughly fourteen screens — the overview, the checks page, the walk page, the release page, the review desk, the fleet roll-up and the rest — and none of them is in the record. Two things this repo just built therefore cannot work on this repo.

A change note's `## Impact` section is supposed to name the screens it altered, one `[[SUR-####]]` link per line. [[CHG-20260914-The-Walk-Page-Reads-As-A-Script]] altered the walk page, the checks page and the design view, and could link none of them — its Impact lines name the screens in prose with a bracketed apology.

The walk's survey reads exactly those lines. So on this repo the survey it just gained will stay empty however many screens a release changes, because no change note here can write a line it can read. The feature is testable here only against fixtures.

## A third thing it breaks, found 2026-09-14

Since [[TASK-0625-The-Checks-Page-Groups-By-Screen]], a `~checks` group whose `area:` matches no surface note carries a "no surface note" badge, so that a surface rename cannot orphan its checks quietly ([[ISS-0250]]). On this repo **all 25 groups carry it**, because there is one surface note and 25 areas. The badge is accurate and useless here: a warning on every row is not a warning.

That is not an argument for softening the badge. It is the same defect as the other two, showing up on a third surface.

## Evidence

```
$ ls docs/surfaces/
SUR-0001-The-Tests-View.md
```

The design view's Surfaces heading, since [[TASK-0625-The-Checks-Page-Groups-By-Screen]], reads `Surfaces · 1 screen · 1 with no checks` — against [[FEAT-0130-Surfaces-Are-A-First-Class-Type]]'s target of 12 to 15 top-level screens.

## Why it is filed rather than fixed, and parked

*(Re-homed to [[PHASE-999-Future]] when PHASE-044 closed. It was found inside that phase and is not its work: writing this repo's surface notes is a job of its own, with no phase yet.)*

Writing fourteen surface notes is not a step inside PHASE-044, whose scope is the walk page reading as a script. Doing it inside this change would be the widening `LIFECYCLE.md`'s "Scope of a change" names: the requested behaviour works without it, on fixtures and on `your-trainer`.

It is worth doing on its own, and it is roughly a session: name the screens, give each a `gallery:` key, and point the existing checks' `area:` strings at them. The payoff is that this repo can then walk its own releases with the page it ships.

## What would close this

- [ ] A `SUR-*` note per top-level screen, with dialogs as children under `parent:` (upstream ADR-0044's four rules, `tools/instructions/TAXONOMY.md`).
- [ ] The design view's Surfaces heading reports a screen count inside FEAT-0130's 12 to 15.
- [ ] A change note in this repo can write an `## Impact` line that resolves.
