---
type: "[[feature]]"
id: FEAT-0148
aliases: ["FEAT-0148"]
title: "One HTML viewer replaces the design bench — any note's page opens in it, and nothing about showing a page is specific to designs"
status: backlog
phase: "[[PHASE-042-A-Note-Shows-What-It-Is-About]]"
owner: user:edwin
created: 2026-09-12
updated: 2026-09-12
source: ["Edwin, 2026-09-12: 'html viewer vs bench, I don't think the current bench provides much ... so I would remove it and instead have a generic html viewer'"]
goal: "Replace the design bench with one viewer that frames any HTML page a note references, so an agent can show Edwin a page without the page having to be a design."
requirements:
  - "[[REQ-0064-One-Viewer-And-One-Rule-About-What-May-Be-Framed]]"
tasks:
  - "[[TASK-0613-A-Generic-HTML-Viewer]]"
  - "[[TASK-0614-Links-Stop-Asking-For-The-Bench]]"
  - "[[TASK-0615-Remove-The-Bench]]"
  - "[[TASK-0616-Intent-After-The-Bench]]"
  - "[[TASK-0617-Register-And-Deck]]"
release: ""
issues:
  - "[[ISS-0300-A-Design-With-No-HTML-Page-Is-Told-It-Has-Nothing-To-Show]]"
  - "[[RISK-0009-A-Design-Verdict-Stops-Naming-What-It-Judged]]"
  - "[[ISS-0056-Offered-Design-Routes-To-Plan-Verdicts]]"
acceptance_exception: ""
acceptance: ""
design: ""
related:
  - "[[FEAT-0042-Design-Bench]]"
  - "[[FEAT-0147-Pictures-Beside-The-Note]]"
  - "[[ADR-0042-What-May-Be-Framed]]"
  - "[[RISK-0008-The-Sandbox-Is-The-Only-Boundary]]"
  - "[[REQ-0062-A-Link-That-Names-A-Design-Opens-The-Design-Bench]]"
  - "[[ISS-0300-A-Design-With-No-HTML-Page-Is-Told-It-Has-Nothing-To-Show]]"
  - "[[RISK-0009-A-Design-Verdict-Stops-Naming-What-It-Judged]]"
  - "[[ISS-0056-Offered-Design-Routes-To-Plan-Verdicts]]"
tags: [feature, render, design, removal]
---

# One HTML viewer

## Goal

Edwin, 2026-09-12: *"I don't think the current bench provides much ... so I would remove it and instead have a generic html viewer."*

A page the cockpit can show should not have to be a design. Replace the bench with a viewer that frames any HTML file a note references, and remove the bench, its endpoints and the machinery around it.

## Scope

### In scope

- A viewer that frames an HTML page referenced by any note, whatever the note's type.
- Removal of the `~design` view, the four `/api/design/*` write endpoints, `/api/cockpit/design-revisions/`, `/api/cockpit/design-comments/`, `/design-asset/` and `/design-asset-at/`.
- Unbinding design verdicts from the bench's endpoint so the **buttons stay on the note**: `VERDICT_ENDPOINTS` loses its `design` entry, `DESIGN_REVIEW_FIELDS` and `design_revision` writing go, and the refusal message naming the old endpoint goes with them.
- Removal of the variant strip, `chosen_variant:` and the Choose-a-variant ADR offer.
- Deciding where the design-ID link rule goes, and superseding [[REQ-0062-A-Link-That-Names-A-Design-Opens-The-Design-Bench]] and [[FEAT-0042-Design-Bench]].
- What the Intent landing shows for designs afterwards.
- The capability register, and telling Deck.
- Removal of the tests that covered the removed feature: `tests/test_design_bench.py` (170 tests, 3,174 lines), and the design-specific parts of `test_design_gate.py` (7), `test_design_variants.py` (11), `test_design_tokens.py` (10).

### Out of scope

- **Side-by-side comparison of two versions.** Deferred by Edwin, and when it is built it must serve `.md` notes too. See the phase note.
- A replacement for region-anchored commenting. Nothing is built to replace it in this feature; the argument is in the table below.
- Images and the attachment convention — [[FEAT-0147-Pictures-Beside-The-Note]].

## What the bench carried, and where each part goes

Measured across 47 design notes in 12 fleet repos on 2026-09-12.

| Capability | Measured use | Where it goes |
| --- | --- | --- |
| Frame an HTML artifact at a declared viewport | 33 of 47 notes declare an `asset:` | **Kept**, as the generic viewer. This is the feature. |
| `## Revisions` log | 6 notes carry real entries (deck DES-0002: 10, your-health DES-0002: 9, this repo's DES-0004: 4) | **Survives for free.** It is Markdown in the note; the note renderer already shows it. Nothing to build. |
| Revision capture (`/api/design/capture`) and side-by-side compare of two shas | The log has 6 users; the capture button wrote some of them | **Retired.** A revision is a commit against the page (`TRACEABILITY.md`, `[[design]]` links) and the reason belongs in the commit message. Writing the log line by hand is one line of Markdown. Compare is the deferred work. |
| Region-anchored comments (`data-design-region`, `/api/design/comment`) | **Used, once, seriously.** 24 artifacts declare regions. 12 region-anchored comments exist fleet-wide, all on `project-os-deck` DES-0002, all written by one reviewer in one pass on 2026-09-05; 4 more comments are document-level. | **Retired, and this one gives something up.** The 16 comments already in notes stay — they are Markdown under `## Review` and the note renderer shows them. What is lost is the anchoring: a new comment can no longer say *which part* it is about except in its own words. One reviewer has ever wanted that, and could have written the same list into the note. If it should come back it is a separate feature with that reviewer's case behind it. |
| Choose-a-variant and the ADR it offers | 1 note uses `## Variant`; `chosen_variant:` set on **0** | **Retired.** Never exercised on a real design. |
| **Accept / Decline on a design** | 7 designs carry a verdict; 3 of those also carry a `design_revision` | **Kept, and it was never the bench's.** The buttons sit on the **note**, from the same actuator table every other type uses. `note_writes.py:239` says so: *"The actuator row still offers the buttons — the vocabulary stays in this table — but they carry the endpoint that has to serve them."* After this, they carry the generic `/api/notes/transition` like a task or an issue. |
| The verdict's binding to a revision (`/api/design/verdict`, `design_revision`) | 3 designs carry a `design_revision`: this repo's DES-0002 and DES-0004, and DES-0009 | **Retired, knowingly, and it re-opens a hazard.** The endpoint's job was to make a verdict name the artifact commit it judged. Dropping it means an approval given to revision 3 silently covers revision 6. Edwin accepted that on 2026-09-12 — *"Drop the binding for now!"* — and **"for now"** is why it is [[RISK-0009-A-Design-Verdict-Stops-Naming-What-It-Judged]] rather than a closed decision. Existing `design_revision:` values stay in their notes. |
| Ask for review (`/api/design/offer-review`) | The bench header button at `renderer.ts:6637` — the one genuinely bench-hosted write | **Retired as an endpoint.** Putting a design on the review desk is the generic path, the same as any other note. |
| The design rows on the Intent landing | The only way to browse designs | **Kept, re-pointed.** [[TASK-0616-Intent-After-The-Bench]]. |
| The note banner button and the bench header's ID chip | Navigation between note and bench | **Re-pointed.** The note gains a link to its page when it has one; the chip goes with the bench. |

**Two corrections to this table, 2026-09-12, both worth seeing rather than silently absorbed.**

The first version said region comments had **never been used**. They have: 12 region-anchored comments exist, and the retirement row now states what is given up instead of implying nothing is.

The first version also retired *"offer-for-review and the design verdict"* as one row, on the reasoning that verdicts are frontmatter and get written directly. Edwin challenged it — *"The only thing about design verdict buttons, why can we not have these, we currently allow for the other items to be triaged and providing review info?"* — and he was right. Accept and Decline for a design were never bench-hosted; they sit on the note, from the actuator table every type shares, and only their **endpoint** was design-specific. The row was describing a removal that was not on the table. It is now three rows: the buttons are kept, the revision binding is retired with its hazard recorded, and `Ask for review` — the one write that really did live in the bench header — is retired.

Removing a feature means removing its tests. It does **not** mean removing its notes: [[FEAT-0042-Design-Bench]], [[REQ-0062-A-Link-That-Names-A-Design-Opens-The-Design-Bench]] and their tasks stay at `superseded`, as the record of what was built and why.

**[[REQ-0023-Design-Is-A-Project-Record]] is not superseded and must not be.** It requires that a design, its revisions and its verdicts live in the repo and remain readable without the tool that renders them. Every one of its four acceptance criteria is still satisfied after this work, and two are satisfied better: annotations and verdicts stay plain Markdown in the note, and no design state was ever held in the cockpit's runtime. Superseding it because its feature is being superseded would discard the one clause that makes this removal safe.

## Upstreaming

Everything in this feature stays local — the viewer, the routes, `renderer.ts`, the capability register, and [[ADR-0042-What-May-Be-Framed]], which is a decision about this application's render surface. The upstream half of the phase is in [[FEAT-0147-Pictures-Beside-The-Note]], and the skill flip there must land **before** [[TASK-0615-Remove-The-Bench]].

Deck consumes this sidecar and is affected without being downstream: `docs/reference/cockpit-capability-register.md` rows `shell.reader.design`, `api.write.design`, `shell.reader.render`, `shell.windows` and `api.infra` all change, and Deck's adoption table at `~/Dev/repos/project-os-deck/docs/reference/cockpit-adoption.md` tracks them. [[TASK-0617-Register-And-Deck]].

## Acceptance

- An HTML page any note references opens in the viewer.
- Nothing in the sidecar or the renderer decides display by the word `design`.
- The eight endpoints are gone; each is re-homed or retired with the reason recorded above.
- A design's Accept and Decline still work, from the note, through `/api/notes/transition` — and no longer write `design_revision`.
- A design's `## Revisions` and `## Review` sections still read in the note.
- The Intent landing still reaches every design.
- The capability register names no removed route.

## Links

- Requirement: [[REQ-0064-One-Viewer-And-One-Rule-About-What-May-Be-Framed]]
- Tasks: [[TASK-0613-A-Generic-HTML-Viewer]], [[TASK-0614-Links-Stop-Asking-For-The-Bench]], [[TASK-0615-Remove-The-Bench]], [[TASK-0616-Intent-After-The-Bench]], [[TASK-0617-Register-And-Deck]]
- Check: [[TST-0087-An-HTML-Page-Opens-In-The-Viewer]]
