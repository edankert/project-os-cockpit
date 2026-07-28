---
type: "[[feature]]"
id: FEAT-0043
aliases: ["FEAT-0043"]
title: "Design as a top-level surface, opening with the project brief"
status: doing
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["user decision 2026-07-28", "measurement:2026-07-28 fleet brief audit"]
goal: "Give design its own top-level mode, positioned before the structure modes, opening with the durable answer to 'what are we building and what should it look like' — so an agent reads it every session and it stays true."
requirements: ["[[REQ-0024-Brief-Is-Maintained]]"]
tasks:
  - "[[TASK-0222-Fill-And-Guard-The-Brief]]"
  - "[[TASK-0223-Brief-Payload-And-Identity-Band]]"
  - "[[TASK-0224-Design-Mode-In-The-Strip]]"
  - "[[TASK-0225-Design-Rationale]]"
release: ""
design: ["[[DES-0002-Cockpit-Design-System]]"]
related: ["[[FEAT-0042-Design-Bench]]", "[[REQ-0022-Overview-State-Above-History]]"]
tests: []
---

# Design as a top-level surface

## Why, with the measurement

`LLM_BRIEF.md` ships in every project-os repo and describes itself as "the machine-oriented project brief". Measured 2026-07-28: **10 of 11 fleet repos still carry `Name: REPLACE ME` and `Purpose: REPLACE ME`.** The only exception was created yesterday, and only because an agent happened to be reading the template at the time.

That file is not failing because nobody needs it. It is failing because **nothing ever shows it**. A file nobody can see is a file nobody maintains.

The same lesson arrived twice more in two days, from the other direction: the design bench was built, tested by 44 tests, and unreachable — first because nothing linked to it, then because the link used a URL shape the nav discards. A surface people cannot find does not get used, and a surface that does not get used does not stay true.

## Scope

- The brief filled in for this repo, and a validator check so a placeholder brief is reported rather than shipped ([[TASK-0222]]).
- A brief payload and identity band: what this is, who for, its shape ([[TASK-0223]]).
- A `design` mode in the strip, **positioned second** — after Overview, before the structure modes ([[TASK-0224]]).
- Design rationale: ADRs a design note *links*, not the whole set ([[TASK-0225]]).

Reading order on the surface: **identity → design system → artifacts → rationale.** What it is, what it should look like, what has been proposed, why it is that way.

## Out of Scope

- **Risks and workflows.** A risk is an operational hazard with no bearing on what the app should be; a workflow is how to run the build. Both are Library material — consulted when relevant, not context you carry.
- **Every ADR.** ADR-0006 (retire the delivered band) is design rationale; ADR-0011 (dated promotion) is process governance. Surfacing all of them would drag governance into a product surface. Only linked ones appear.
- **Widening Overview.** It already carries focus, counts, phases, waiting-on-you, activity and commits, and [[REQ-0022]] pins it to fitting above the fold at 900px. Identity there costs the thing that requirement protects.

## Acceptance

- The strip carries seven modes with `design` second; an existing stored mode preference still resolves.
- The surface opens with this repo's real identity — not a placeholder.
- A brief still carrying `REPLACE ME` is reported by the validator, and the surface says so rather than rendering it.
- Only ADRs linked from a design note appear; the rest stay in Library.
- The design system and artifacts remain reachable in one click, as they are now.

## The ordering argument

The strip encodes *kinds of thing*, not frequency: state · structure ×3 · queue · record. Design sits **upstream of structure** — what it should be, before what is being built — so `overview · design · features · tasks · issues · review · library` reads as a progression rather than a list.

Worth stating plainly: Active and Recent were retired two days ago on the reasoning that six modes was the ceiling. Going to seven is a deliberate reversal of that ceiling, not a drift, and it is justified by the brief being read every session rather than browsed occasionally.

## Links
- Phase: [[PHASE-009-Design-Surfaces]]
- Requirement: [[REQ-0024-Brief-Is-Maintained]]
- Consumes: [[FEAT-0042-Design-Bench]]
