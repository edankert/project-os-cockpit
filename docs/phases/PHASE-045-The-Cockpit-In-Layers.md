---
type: "[[phase]]"
id: PHASE-045
aliases: ["PHASE-045"]
title: "The cockpit in layers — the first screen shows the least a person needs, and every flow shows more only on request"
status: planned
order: 45
owner: user:edwin
created: 2026-09-17
updated: 2026-09-17
goal: "A person opening a project sees what needs them, what is in flight and how far the work has travelled on one screen of a few kilobytes, and reaches the design, build, verification and issue flows one layer at a time, with the record behind a fold. Opened as a place to refine that idea, not as a commitment to build it."
features:
  - "[[FEAT-0152-Home-First]]"
  - "[[FEAT-0153-Flows-As-Views]]"
  - "[[FEAT-0154-Subject-Threads]]"
requirements: []
tasks: []
issues: []
related:
  - "[[DES-0015-The-Cockpit-In-Layers]]"
  - "[[REFERENCE-FUTURE-COCKPIT-ENHANCEMENTS]]"
  - "[[DES-0001-Overview-Redesign]]"
  - "[[DES-0008-The-Returning-Human]]"
  - "[[ADR-0020-Obligations-Live-With-Their-Subject]]"
  - "[[ADR-0025-An-Owed-Row-May-Appear-Twice]]"
  - "[[ADR-0028-Work-Has-Three-Phases]]"
  - "[[PHASE-016-The-Overview-Answers-Questions]]"
  - "[[PHASE-026-The-Returning-Human]]"
  - "[[PHASE-030-Obligations-Go-Home]]"
  - "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
tags: [layers, overview, navigation, design]
---

# The cockpit in layers

## Goal

A person opening a project sees four facts and one sentence: what needs them, what is in flight, whether an agent is working, and how far the work has travelled. Everything else sits one layer down, reached one click at a time, and the raw record sits behind a fold. The four flows the project already runs (design and review, implementation, verification, issue triage) keep their subjects, their verbs and their write paths; what changes is how much of each flow is on screen at once.

The design is [[DES-0015-The-Cockpit-In-Layers]], offered on 2026-09-17 and not yet accepted. **This phase exists so that design can be refined over time.** Edwin, 2026-09-17: *"I am not fully convinced, so document it in such a way that we can refine over time."* So the phase is `planned`, its features are `backlog`, and its exit criteria are about decisions being made and recorded, not about screens being built. It becomes `active` when Edwin accepts the design, or one revision of it, and picks a first feature.

**Why a phase.** The goal is stated without listing its parts, and the exit criteria are not "the tasks are done" (CLAUDE.md, "When to open a phase"). Three earlier phases shaped this surface and each answered one question: [[PHASE-016-The-Overview-Answers-Questions]] made every number lead somewhere, [[PHASE-026-The-Returning-Human]] gave the person who was away a digest, and [[PHASE-030-Obligations-Go-Home]] put every obligation in the view that owns its subject. This phase asks the question none of them did: how much should be on the screen at all.

## The idea, in one paragraph

Five layers of data. **L0, glance**: four facts per project on the rail square, the fleet page and a Dock badge. **L1, Home**: three cards (Needs you, In flight, Shipping), one line for "since you looked", the active phase as one row. **L2, flow**: four views, Design, Build, Verify, Issues, each listing subjects by state with finished work folded to a count. **L3, subject**: a feature, design, issue or release as a header card, a timeline of what happened and the note. **L4, record**: raw frontmatter, ledger, validator, sessions, commits, on demand. Each click adds one level. Measured on 2026-09-17, the first screen loads 772 KB here and 1.06 MB on your-trainer, while everything that needs a person fits in 1.1 KB. The design's Plate 1 is the table; its "four flows, layer by layer" table says what each flow shows at each layer.

## Scope

Three features, one per option in the design, in the order the design recommends. Each can ship alone and each can be declined alone.

- [[FEAT-0152-Home-First]] (option C): L0 and L1. The four facts on the rail and a Dock badge; Home replaces the overview's first screen; the overview's tiles, phases and history move under Record. Additive and reversible.
- [[FEAT-0153-Flows-As-Views]] (option A): L2. The navigator's modes become Home, Design, Build, Verify and Issues, each ordered by state with terminal groups folded and fetched on demand. Reopens part of [[ADR-0028-Work-Has-Three-Phases]] (see D2 below), so it opens on a decision.
- [[FEAT-0154-Subject-Threads]] (option B): L3. A subject page with a header card, a timeline and folded agent sessions; the sidebar lists subjects by recency and need. The largest renderer change, and possibly Deck's to build rather than this repository's.

Refining the design is in scope: a revision of [[DES-0015-The-Cockpit-In-Layers]] is a commit against the note and its plates, logged in its Revisions section and in the refinement log below.

## Out of Scope

- Any new status, any new write path, any verdict written by a machine. Every button the design draws is a registry verb that exists.
- The panel and window architecture, the 2D desk and the glass field ([[project-os-deck#REFERENCE-SURFACE-ARCHITECTURE-OPTIONS]]). This phase changes payloads and pages, not the pane grammar.
- The sidecar's own tablet HTML (mode 1). [[ADR-0010]] gates its parity on an authenticated write path.
- The Obsidian vault profile ([[ISS-0279]]).
- Repairing the record. Home will say "no run recorded" and "no surface note" where those are true; making them false is data work under [[ISS-0306]] and its kin, not presentation.

## Open decisions

These are the design's D1 to D5, kept here because the phase owns them until each is decided. A decided one gets a date, Edwin's words, and where the decision was recorded (the design's Review section, or an ADR when it reopens an earlier ruling).

| id | question | the design recommends | status |
| --- | --- | --- | --- |
| D1 | Does Home replace the overview, or sit beside it? | replace; the overview's contents keep their pages under Record | open |
| D2 | Do the four flows become the navigation, and where does the publication ladder live? | Home, Design, Build, Verify, Issues, with commits and the release on Home's Shipping card and in Verify's "This release"; this narrows [[ADR-0028-Work-Has-Three-Phases]], which gave publication its own view, and needs an ADR | open |
| D3 | What does the Dock badge count? | the fleet's needs-you total (89 on 2026-09-17), because the badge is the only glance a person gets while the window is hidden | open |
| D4 | Is "Duplicate of" a triage disposition worth a button? | yes, as `declined` plus a `related:` link, no new status | open |
| D5 | Do agent sessions fold by default on subject pages while the strip stays live? | yes; the strip answers "is an agent working", the fold answers "what did it do" | open |

Edwin's stance on the whole, 2026-09-17: *"I am not fully convinced."* No decision above is presumed.

## Exit Criteria

Written so the phase can close on a refusal as honestly as on a build.

- [ ] [[DES-0015-The-Cockpit-In-Layers]] carries a verdict from Edwin in its frontmatter: `accepted`, or `changes-requested` followed by a revision that is then accepted, or `cancelled`. If cancelled, this phase closes as `superseded` by whatever note records the alternative, or `deferred` if there is none.
- [ ] D1 to D5 are each decided and recorded: in the design's Review section, or in an ADR where the decision narrows an accepted one (D2 narrows [[ADR-0028-Work-Has-Three-Phases]]).
- [ ] The layer budgets in the design's Plate 1 are measured on every repository the shell discovers, not only on this one and your-trainer, and the design's table is corrected where the fleet disagrees.
- [ ] Each of the three features is either built and walked, or declined with the reason in its own note. Declining one does not block the others.
- [ ] Whatever is built passes the design's ten-second test on Edwin's real data, recorded as an acceptance check: the person names the next decision, the in-flight item and the release blocker within ten seconds of opening a project, and the first screen loads under 50 KB.
- [ ] Nothing built adds a status, a write path or a machine-written verdict, and the capability register names every new or changed row.

## How to refine this

- **To change the proposal**, edit [[DES-0015-The-Cockpit-In-Layers]] and its plates, add a line to its Revisions, and add a dated line to the log below saying what changed and why. One revision per commit.
- **To raise a question**, add a row to Open decisions with a new id and leave its status `open`.
- **To decide something**, fill the status column with the date and Edwin's words, and record it where the table says.
- **To try one option without committing to the model**, move that feature to `planned` and set `focus.feature`; the phase becomes `active` with it. The other two stay `backlog`.
- **To give up on it**, cancel the design and close this phase as `deferred` or `superseded`; the measurements in the design stay true either way.

## Refinement log

- 2026-09-17 — Opened as `planned` on Edwin's instruction: *"Document this fully as a new phase. (I am not fully convinced, so document it in such a way that we can refine over time)."* The design was offered the same day with seven mockup plates and four as-built captures, measured against this repository and your-trainer. Three features scaffolded at `backlog`, one per option. Nothing built. Focus stays on TASK-0631, which belongs to another session.

## Notes

- The first thing to refine is probably the L1 card set. The design chose three cards (Needs you, In flight, Shipping) from the four facts; a fourth card for the active phase was folded to one row. If the fleet's repos without releases make the Shipping card mostly empty, it should collapse to the commits line, and that is a design revision rather than a feature change.
- The design's option B may belong in Deck. If Edwin decides so, [[FEAT-0154-Subject-Threads]] is `superseded` by a Deck note and this phase's scope shrinks to C and A without changing its goal.
- Yesterday's reference note, [[REFERENCE-FUTURE-COCKPIT-ENHANCEMENTS]], lists seven proposals from the same walk; this phase adopts proposals 1, 2, 5 and 6 through the design and leaves 3, 4 and 7 where they are.
