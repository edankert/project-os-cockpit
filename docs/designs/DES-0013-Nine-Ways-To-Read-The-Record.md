---
type: "[[design]]"
id: DES-0013
aliases: ["DES-0013"]
title: "Nine ways to read the record — nine applications over one corpus, differing by navigation rather than by theme"
role: proposal
decided: ""
status: "proposed"
phase: "[[PHASE-028-Borrowed-Capability]]"
owner: user:edwin
created: 2026-09-05
updated: "2026-09-05"
source: ["Edwin 2026-09-05: 'I would like to explore some more crazy ideas and applications / visualisations that we could build on-top of this ... I would like you to design 9 totally different applications, they really need to be totally different, they should look differently and allow for different style of navigation and interaction ... not different themes, actually different applications'"]
asset: "DES-0013-nine-ways-to-read-the-record.html"
implements: []
supersedes: ""
superseded_by: ""
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[PHASE-028-Borrowed-Capability]]", "[[FEAT-0080-The-Harness-Survey]]", "[[DES-0002-Cockpit-Design-System]]", "[[ADR-0020-Obligations-Live-With-Their-Subject]]", "[[DESIGN]]"]
tags: [design, survey, exploration]
---

# Nine ways to read the record

> **Nothing here is accepted and nothing is scheduled.** This is a proposal at the widest end of [[PHASE-028]]'s standing survey: nine applications that could stand on the corpus the cockpit already indexes, drawn far enough to be argued with. Two of them contradict decisions this project has already taken, and those two say so on their own plate rather than in a footnote.

## Problem

**The cockpit has one shape, and it is a reader.** Three panes, a document in the middle, a rail of workspaces: the shape you use to *read* a record and *discharge* what it owes. It is the right shape for that, and [[DESIGN]] is the argument for why.

It is not the only shape the data supports, and nothing in the repo says what the others would be. The corpus, measured today:

| what | count |
| --- | --- |
| notes under `docs/` | 1537 |
| `[[wikilinks]]` between them | 16148 |
| distinct link targets | 2206 |
| notes created per month, 2026-05 → 09 | 180 / 1 / 313 / 634 / 6 |
| notes carrying `review_verdict: changes-requested` | 70 |
| …of those, already at a terminal status | 61 |

Two of those rows are the argument for this note. **16148 links over 1537 notes is a graph nobody has ever seen** — the cockpit resolves a wikilink when you click it and shows backlinks on the note, which is the local view of a structure that has never been drawn whole. And **the month histogram has a hole in it**: one note in June, against 180 in May and 313 in July. No current surface makes that visible, because every surface is scoped to a note, a phase or a queue, and a silence belongs to none of them.

*(The 70/61 row also updates a measurement `CLAUDE.md` records as 49/43 on 2026-08-20. The stale-verdict backlog has grown by 21 in sixteen days. That is a finding this exercise produced by accident, and it belongs in an issue rather than in a design — noted here only because the number appears in the artifact.)*

## Approach

**Nine applications, separated on six axes, one corpus underneath.** The brief was that they be different *applications* rather than different *themes*, so the artifact opens with the matrix that makes that claim checkable: dimension, who decides the layout, which slice of time, primary input, venue, and the verb the user is performing. Two designs that land on the same row of that matrix are one design wearing two skins, and the matrix is where that is caught.

| # | name | what it is | the verb |
| --- | --- | --- | --- |
| 1 | **ORBIT** | the 16148 links as a solid you fly through, coloured by status band | explore |
| 2 | **ATLAS** | the corpus as land with fixed coordinates you learn by heart | locate |
| 3 | **REEL** | the project as a scrubable timeline that reconstructs any past instant | reconstruct |
| 4 | **PULSE** | live agent sessions as an instrument wall for a second screen | supervise |
| 5 | **ASK** | the record as a branching conversation with citations | interrogate |
| 6 | **DECK** | one obligation at a time, dealt as cards, to zero | discharge |
| 7 | **LEDGER** | every note as a row, faceted, sortable, bulk-editable | query |
| 8 | **BROADSHEET** | the week auto-typeset as a newspaper, for paper or e-ink | read |
| 9 | **FOUNDRY** | work as a factory floor where the bottleneck is physically visible | unblock |

Each plate in the artifact carries a mock, the navigation model, the data it would need — separated into endpoints that exist today and what would have to be built — and the strongest objection to building it. The objection is part of the design, not an appendix: a proposal that cannot state its own weakest point has not been argued.

**The mocks use measured numbers.** Every count, every date span and every ID in the artifact is this repo's. The month histogram under REEL's ruler is the 180/1/313/634 above, so the June silence is visible in the mock rather than described in prose.

## Regions

Fifty regions. Each of the nine plates carries five — the plate itself, then its mock, navigation, data and objection — so a reviewer can object to *how it is drawn* separately from *what it would cost* and from *whether it should exist at all*. Those are three different arguments and they were collapsing into one.

- `masthead` — the framing: what this is, what it is not, and that nothing is accepted
- `matrix` — the six-axis separation table; the check on "these are nine applications, not nine themes"
- `orbit`, `atlas`, `reel`, `pulse`, `ask`, `deck`, `ledger`, `broadsheet`, `foundry` — one per plate, for a comment about the concept as a whole
- `<plate>-mock` — the drawing, for a comment about what is on screen
- `<plate>-navigation` — the claimed interaction model, which is what separates each design from the other eight
- `<plate>-data` — what exists today against what would have to be built
- `<plate>-objection` — the strongest argument against building it, mine unless stated
- `not-drawn` — seven concepts considered and rejected, each with the reason
- `first-build` — which two are worth a prototype, and the order
- `incidental-finding` — the stale-verdict measurement, which is not a design and says so

## Tokens

**Status and severity are the implementation's, verbatim** from `src/project_os_cockpit/static/base.css` — `--status-active`, `--status-pending`, `--status-done`, `--status-archived`, `--status-blocked`, `--status-reference` and the four `--severity-*`. Light values are declared first, because `design_tokens.read_tokens` takes the first declaration and a dark-block-first artifact would be compared against the wrong scheme.

Everything else in the artifact is its own chrome and is **not** a specification. The dossier's editorial palette (`--paper`, `--ink`, `--rule`, `--accent`) exists to frame nine mocks that must not look alike, and each mock declares a scoped local palette under its own selector (`.m-orbit`, `.m-atlas`, …). Those are illustration. If any of the nine is ever built, its palette is designed then, against [[DES-0002]].

## Out of scope

- **Choosing.** Nine proposals, no recommendation ranking beyond `first-build`, and no feature, task or phase allocated.
- **Feasibility beyond the data.** Each plate names the endpoints it would need; none estimates effort, and no plate has been checked against what the sidecar can actually serve at 1537 notes.
- **The cockpit's own shape.** Nothing here proposes changing the three-pane reader. These are applications *beside* it, over the same corpus.
- **Mobile.** [[FEAT-0079]] owns supervision from a phone; DECK is drawn at a phone's proportions but does not restate that feature's boundary.

## Revisions

- 2026-09-05 — written; nine plates, fifty regions

## Review

<Region-anchored comments land here. Verdicts go in the frontmatter, transcribed from a review that actually happened — never anticipated.>
