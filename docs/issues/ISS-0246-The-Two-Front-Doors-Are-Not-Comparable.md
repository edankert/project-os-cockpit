---
type: "[[issue]]"
id: ISS-0246
aliases: ["ISS-0246"]
title: "The browser cockpit has two views and the desktop shell has twelve — ADR-0010 decided parity and gated it on an authenticated write path that does not exist, and `both front doors` has been quoted since as though parity already applied"
status: open
owner: user:edwin
created: 2026-08-20
updated: "2026-08-20"
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: approved
source: ["measured while closing TASK-0511, 2026-08-20"]
severity: high
component: cockpit
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[ISS-0230-The-Browser-Cockpit-Has-No-Surface-Row]]", "[[PHASE-029-One-Tool-Two-Front-Doors]]", "[[ADR-0010-Two-Front-Doors]]", "[[TASK-0511-A-Picker-Writes-Features-And-Phases]]"]
tests: []
---

# The rule assumes a symmetry that has never existed

## Measured 2026-08-20

Virtual pages (`~name` routes) implemented in each front door:

| front door | pages |
|---|---|
| `desktop/src/renderer/renderer.ts` | **12** — `~agents`, `~checks`, `~design`, `~features`, `~history`, `~inbox`, `~issues`, `~overview`, `~publication`, `~release`, `~review`, `~tests` |
| `src/project_os_cockpit/static/cockpit.js` | **2** — `~note`, `~root` |

The browser cockpit renders **notes and a navigator**. Every view this phase has been about — the tests view, the checks page, the release page, the design view — exists in the desktop shell alone.

## Why this matters now

[[PHASE-029]] states the rule: *"the browser cockpit and the desktop shell answer the same questions, and differ only where a difference was decided."* [[ISS-0230]] applied it and was fixed — correctly, for a **row renderer** that both files genuinely have.

But the rule has since been reached for repeatedly on things only one door has. [[TASK-0511]] closed with *"the browser cockpit does not have this control"* as a follow-up, on the assumption that adding it was a small matter of a second call site. **It is not**: the control lives on a release page the browser cockpit does not have, and building it means building the twelfth view rather than the picker.

So the obligation has been carried, note to note, in a form nobody can discharge — and each time it is deferred it reads as an omission rather than as the decision it actually needs.

## Corrected 2026-08-20 — the decision WAS taken, and I said it was not

This note first claimed *"[[ADR-0010]] is `proposed` … the decision has never been taken."* **It is `accepted`, `decided_option: "4"`, decided 2026-08-12** — and I asserted otherwise without opening it. Filing an issue about unread premises on an unread premise.

**Option 4 is *parity, gated on an authenticated write path*.** *(This repo's [[ADR-0010]] — `What the browser cockpit is for`. `project-os-dev` carries a different `ADR-0010`, and an unqualified link resolved to the wrong one for the reviewer; the fleet has two.)* Edwin confirmed parity again on 2026-08-20 when asked, which is consistent rather than new. The ADR's own words: *"The browser cockpit is the reading surface **for now**, and that is a **stage rather than a property**."*

So the twelve-against-two gap is not an undecided question. It is **the decision's own precondition, unmet**:

> *"The loopback check is not a safety feature on top of an authorisation model. It **is** the authorisation model."* — [[REL-0001]]'s acceptance pass drove every mutation endpoint over the real LAN: **ten of ten returned 403 while reads returned 200** ([[REQ-0027]], [[RISK-0005]]).

## What is actually owed, in order

1. **An authenticated write path.** Until a surface can prove *who* is asking, the loopback check cannot be replaced — only removed, which hands every device on the Wi-Fi the ability to transition notes and create files across twelve repos. This is the gate, and nothing below it can start.
2. **The eleven reading views**, which the ADR does **not** gate: `~overview`, `~features`, `~issues`, `~tests`, `~checks`, `~design`, `~history`, `~agents`, `~inbox`, `~publication`, `~review` answer questions without changing anything. These are owed now, and [[PHASE-029]] is `planned` and empty of them.
3. **The writing surfaces** — `~release` and the marks, ticks and pickers — after (1).

## What this issue keeps

The real defect stands, narrowed: ***both front doors* has been quoted as though parity already applied.** [[TASK-0511]] deferred its picker as a small follow-up when the picker's page does not exist there and, under the ADR, could not be written there yet even if it did. Each such deferral reads as an omission rather than as a precondition nobody has met.

## Done when

- [x] The decision is found and read. It exists; the error was mine.
- [x] [[PHASE-029]] carries the eleven reading views as scoped work — recorded on [[FEAT-0083]], with the order, the two already planned, and the three views whose **write** halves stay behind the auth gate.
- [x] Notes carrying a *both front doors* obligation say which stage they wait on.

  **Four, not twenty-five.** The phrase appears in 25 notes; 21 are `done`/`fixed`/`merged` records where it describes what was *done*, and annotating those would be the second-encoding defect this phase spent itself removing. The live ones are [[FEAT-0084]], [[TASK-0364]], [[TASK-0365]] and [[REQ-0032]] — each now names its stage, with `REQ-0032` naming all three because it is the requirement the stages serve.
- [ ] `RISK-0005`'s ten-of-ten measurement is re-run before any write endpoint is offered on a LAN-reachable surface.

## Done when

- [ ] The decision is taken — [[ADR-0010]] accepted, amended or declined, saying which pages the browser cockpit owes.
- [ ] Notes that carry a *both front doors* obligation are re-read against it: [[TASK-0511]]'s follow-up is the live one.
- [ ] Whatever is decided, the rule stops being quoted at pairs where only one side has the surface.

## Independent review — third pass, 2026-08-20

Fresh context, separate session, `model:claude-opus-5`, reviewing `6cc7f72..HEAD`. Verdict: **approved**. Every claim below was re-measured or re-executed.

Re-derived and correct on every point I could check.

- **`ADR-0010` is `accepted`, `decided_option: "4"`** — verified in `docs/decisions/ADR-0010-What-The-Browser-Cockpit-Is-For.md`. The self-correction is right.
- **The stage decomposition is faithful to option 4**, not read into it. Decision 4 says *"REQ-0034 is the unlock, and it gates PHASE-029"* (the auth write path is the gate); decisions 1–2 grant the Overview and the read-only Design register **now** (the reading views are ungated); decision 3 keeps every actuator mode-3 (the writing surfaces come after). Three stages, each with a sentence in the ADR behind it.
- **12 against 2 reproduces.** `cockpit.js` implements exactly `~note` and `~root`. `renderer.ts` matches 17 `~` routes, of which the note's 12 are the views; the other five (`~accept`, `~note`, `~root`, `~session`, `~sweep`) are addressing and sub-page routes. The curation is defensible but the note does not say it curated — worth one clause.
- **The four annotated notes are the right four.** `FEAT-0084`, `TASK-0364`, `TASK-0365` and `REQ-0032` are the live ones; annotating the 21 terminal records would have been the second-encoding defect this phase spent itself removing.

One hazard for a later reader: **there are two different `ADR-0010`s in the fleet** — this repo's *What the browser cockpit is for*, and `project-os-dev`'s *Test status is stamped by execution*. This note links `[[ADR-0010]]` unqualified. I resolved to the wrong one first.
