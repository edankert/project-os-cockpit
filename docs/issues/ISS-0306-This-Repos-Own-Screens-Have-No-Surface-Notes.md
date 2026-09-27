---
type: "[[issue]]"
id: ISS-0306
aliases: ["ISS-0306"]
title: "Most of the cockpit's own screens have no surface note, so every checks group shows a 'no surface note' badge and a change note here cannot link the screen it changed"
status: open
phase: "[[PHASE-999-Future]]"
owner: user:edwin
created: 2026-09-14
updated: "2026-09-27"
reported_by: agent
source: ["Found writing [[CHG-20260914-The-Walk-Page-Reads-As-A-Script]]: its Impact section could name no screen id."]
severity: medium
component: docs
parent: ""
related: ["[[FEAT-0130-Surfaces-Are-A-First-Class-Type]]", "[[TASK-0625-The-Checks-Page-Groups-By-Screen]]", "[[CHG-20260914-The-Walk-Page-Reads-As-A-Script]]", "[[ISS-0250-A-Surface-Rename-Silently-Orphans-Its-Checks]]"]
tests: []
tags: [issue, surfaces, walk]
---

# Most of the cockpit's own screens have no surface note

The cockpit has about fourteen screens but only four surface notes, so on this repo the checks page marks nearly every group 'no surface note', and the release test page's list of changed screens stays empty.

## Problem

`docs/surfaces/` holds exactly one note, `SUR-0001-The-Tests-View`. The cockpit has roughly fourteen screens — the overview, the checks page, the release test page, the release page, the review desk, the fleet roll-up and the rest — and none of them is in the record. Two things this repo just built therefore cannot work on this repo.

A change note's `## Impact` section is supposed to name the screens it altered, one `[[SUR-####]]` link per line. [[CHG-20260914-The-Walk-Page-Reads-As-A-Script]] altered the release test page, the checks page and the design view, and could link none of them — its Impact lines name the screens in prose with a bracketed apology.

The release test's list of what changed reads exactly those lines. So on this repo the list it just gained will stay empty however many screens a release changes, because no change note here can write a line it can read. The feature is testable here only against fixtures.

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

Writing fourteen surface notes is not a step inside PHASE-044, whose scope is the release test page reading as a script. Doing it inside this change would be the widening `LIFECYCLE.md`'s "Scope of a change" names: the requested behaviour works without it, on fixtures and on `your-trainer`.

It is worth doing on its own, and it is roughly a session: name the screens, give each a `gallery:` key, and point the existing checks' `area:` strings at them. The payoff is that this repo can then test its own releases with the page it ships.

## What would close this

- [ ] A `SUR-*` note per top-level screen, with dialogs as children under `parent:` (upstream ADR-0044's four rules, `tools/instructions/TAXONOMY.md`).
- [ ] The design view's Surfaces heading reports a screen count inside FEAT-0130's 12 to 15.
- [ ] A change note in this repo can write an `## Impact` line that resolves.

## Checked against the code, 2026-09-19: still true, kept

**What a user notices:** On this repo's checks page nearly every group carries the "no surface note" badge, so the badge warns about nothing. A change note cannot link the screen it changed, and the release test's list of changed screens has nothing to show.

Evidence: `ls docs/surfaces/` now shows four notes (SUR-0001 The Tests View, SUR-0002 The Desktop Console, SUR-0003 Account Usage, SUR-0004 The Release Walk), up from one, against about fourteen screens. All four have `gallery: []`. The test notes use 25 distinct `area:` values (`grep -h "^area:" -r docs/tests | sort -u | wc -l`), and only three surface notes carry an `area:`.

Bigger: roughly a session of note writing. Name each top-level screen, give it a `gallery:` key, and point the existing checks' `area:` strings at them.

**Belongs to:** no open feature (FEAT-0130, which made surfaces a note type, is done). **Next:** write the remaining surface notes as one docs task.

Checked as part of project-os-dev FEAT-0036 (TASK-0141).
