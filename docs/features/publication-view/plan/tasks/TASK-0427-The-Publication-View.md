---
type: "[[task]]"
id: TASK-0427
aliases: ["TASK-0427"]
title: "The Publication view — a nav mode over the ladder, with `~history` re-homed inside it rather than replaced"
status: done
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["Edwin 2026-08-16, choosing the name: 'Publication'"]
parent: "[[FEAT-0102-Publication-Becomes-A-View]]"
effort: M
depends: ["[[TASK-0426-The-Ladder-As-Data]]"]
blocks: []
related: ["[[ISS-0168]]", "[[FEAT-0100-Unpushed-Work-Needs-A-Person]]"]
tests: ["[[TST-0027-The-Ladder-Is-Non-Empty-In-Every-Repo]]"]
---

# The Publication view

## What

`publication` joins `NAV_MODES`, rendering the ladder from [[TASK-0426]]. It is the third phase surface: Intent answers *what is this project*, the work views answer *what are we building*, this answers *how far has it travelled and what is between it and shipping*.

## `~history` is re-homed, not replaced

`~history` is a route today and the overview links to it. It keeps working and becomes an address **inside** the mode. `MODE_ALIASES` records the cost of getting this wrong: a stale client asked for `tests`, silently got the features tree, and the view looked broken for 33 hours. Any id that resolved yesterday resolves tomorrow.

The Push button already lives with the commits it publishes ([[ISS-0168]]) and moves with them unchanged — including the refresh that issue added, which is the part that was missing the first time.

## Definition of done

- [ ] `publication` is a nav mode; its button is present in every workspace
- [ ] The view renders every rung the payload carries, in ladder order, and nothing for a rung the repo cannot reach
- [ ] Non-empty in all 12 discovered repos — walked, not asserted from fixtures
- [ ] `~history` and `~history/<date>` still resolve; a stored preference or deep link migrates rather than stranding the reader
- [ ] The Push action behaves exactly as it does today, including refreshing the surfaces it just changed ([[ISS-0168]]'s repair travels with it)
- [ ] Undeployed commits are named with their reason and **offer nothing**; there is no path from this view that can push a deploy remote
- [ ] The view owns no obligation vocabulary — nouns and verbs ship from the server ([[TASK-0357]]'s rule)
- [ ] A repo that reaches only rung 1 renders a view that reads as complete rather than as broken
