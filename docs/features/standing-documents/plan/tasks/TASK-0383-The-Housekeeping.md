---
type: "[[task]]"
id: TASK-0383
aliases: ["TASK-0383"]
title: "DASHBOARD.md is removed, PHASES.md gains frontmatter and loses a false claim, and the two lying `updated:` dates are corrected"
status: backlog
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-10
updated: 2026-08-10
source: ["[[ISS-0125-The-Singleton-Documents-Have-No-Lifecycle-And-No-Home]]"]
parent: "[[FEAT-0091-The-Standing-Documents]]"
effort: S
due: ""
depends: []
blocks: []
related: ["[[ADR-0004-Cockpit-Code-Driven-Vs-Bases]]"]
tests: []
---

# The housekeeping

## Definition of Done
- [ ] `docs/DASHBOARD.md` is removed, and the `dashboard` type has no members left
- [ ] `docs/PHASES.md` carries frontmatter, and no longer claims to be *"consumed by Bases / dashboards"*
- [ ] `GLOSSARY.md` and `ARCHITECTURE.md` carry `updated:` dates that match their actual last edit
- [ ] `GLOSSARY.md`'s item-type list includes `DES`
- [ ] Nothing references the removed file

## Steps
- [ ] Remove `DASHBOARD.md`; check inbound references first — `docs/README.md` names several of these by path
- [ ] Give `PHASES.md` frontmatter and fix the consumption claim
- [ ] Correct the two dates and the type list

## Notes
**Why the dashboard goes** (Edwin, 2026-08-10): it is an Obsidian artifact, and its six `.base` embeds are all dead — the repo holds `NAVIGATION.base` and `CONTEXT.base`, which are the two that matter (left-hand nav, right-hand context), and it names neither correctly. [[ADR-0004]] deliberately kept `.base` files for Obsidian, so it was legitimate when written; the bases it points at have since gone.

**The two dates are the same slip twice**, which is what makes them worth fixing rather than shrugging at: `GLOSSARY.md` says 2026-05-07 while carrying the ISS-0078 correction written on 2026-07-30, and `ARCHITECTURE.md` says 2026-05-07 while describing a desktop shell that did not exist then. Both were edited without their date being touched — which is precisely what [[TASK-0381]]'s freshness check will read.

`ARCHITECTURE.md`'s diagram is still the original Python server and is not this task's to rewrite; making its staleness *visible* is the feature's job.
