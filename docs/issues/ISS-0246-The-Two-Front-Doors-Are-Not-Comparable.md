---
type: "[[issue]]"
id: ISS-0246
aliases: ["ISS-0246"]
title: "The browser cockpit has two views and the desktop shell has twelve — ADR-0010 decided parity and gated it on an authenticated write path that does not exist, and `both front doors` has been quoted since as though parity already applied"
status: fixed
owner: user:edwin
created: 2026-08-20
updated: "2026-08-20"
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: changes-requested
source: ["measured while closing TASK-0511, 2026-08-20"]
severity: high
component: cockpit
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[FEAT-0083-The-Browser-Cockpit-Answers-Questions]]", "[[RISK-0005-The-Write-Surface]]", "[[ISS-0230-The-Browser-Cockpit-Has-No-Surface-Row]]", "[[PHASE-029-One-Tool-Two-Front-Doors]]", "[[ADR-0010-What-The-Browser-Cockpit-Is-For]]", "[[TASK-0511-A-Picker-Writes-Features-And-Phases]]"]
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

  **Four annotated, and the arithmetic behind that was wrong** *(corrected, independent review fourth pass)*. The phrase appears in 25 notes. I said **21 terminal, 4 live**; it is **17 terminal, 8 live**. The four I annotated — [[FEAT-0084]], [[TASK-0364]], [[TASK-0365]], [[REQ-0032]] — were chosen on a narrower test than the one I stated: *is this a live parity obligation*, not *is this non-terminal*.

  The other four live notes are `CHG-20260820-The-Suite-Is-The-Verdict` (a change record, `active` because change notes do not close), [[TST-0073]] (a test whose subject is the vocabulary, not the doors), [[ISS-0240]] (`tier:` in sort and delta — it mentions the doors, it does not wait on them), and **this note**.

  So the annotation set stands and the stated rule did not. Recorded rather than either widening the annotation to notes that owe nothing or quietly restating the rule to fit the four already chosen — the narrower test is the right one, and it should have been the one written down.
- [~] `RISK-0005`'s ten-of-ten measurement is re-run before any write endpoint is offered on a LAN-reachable surface. — **Re-homed, not performed.** It is a precondition on work that has not started, and this issue could not discharge it: there is no new write path to measure. [[RISK-0005]] now carries it explicitly, beside the trigger that already named the moment (*"any proposal to let mode 1 write"*) and the position that the risk **re-opens before [[REQ-0034]] is implemented, not after**.

## A second `Done when` block outlived the correction above it

**Struck 2026-08-20.** This note carried two `## Done when` sections. The lower one was the original, written before the [[ADR-0010]] correction, and its first item read *"The decision is taken — ADR-0010 accepted, amended or declined."* The section sixty lines above it — *"Corrected 2026-08-20 — the decision WAS taken, and I said it was not"* — answers that item, and the note went on carrying both. A reader following the note's own list was sent to take a decision that had been `accepted` on `decided_option: "4"` since 2026-08-12.

Its three items, and where each actually stands:

| original item | where it went |
|---|---|
| *the decision is taken* | Already taken. It is item 1 of the live list above, and the note's own correction section says so. |
| *notes carrying a `both front doors` obligation are re-read* | Item 3 of the live list, done — four notes annotated, with the population arithmetic corrected after the fourth review (25 carry the phrase, 17 terminal, 8 live). |
| *the rule stops being quoted at pairs where only one side has the surface* | This is the defect itself, and it is what closing this issue records as fixed. |

**It is the same shape this phase keeps finding** — a superseded statement left standing beside the one that supersedes it, in one note, where a reader can reach either. [[FEAT-0083]] carried the identical defect in its `Scope`/**Out** list and was split for it on the same day.

## Fixed 2026-08-20 — the scope exists, so the obligation can be discharged

**What this issue actually asked for was a place to put the answer**, and [[FEAT-0083]] is now it. That note records, as scope rather than as a wish:

- the measurement — **12** virtual pages in `renderer.ts` against **2** in `cockpit.js`, re-derived by independent review;
- [[ADR-0010]] `accepted` on **option 4**, parity gated on an authenticated write path, decided 2026-08-12;
- the split that follows from it — **eleven reading views owed and ungated**, `~release` gated because it composes contents, and the **write halves** of `~checks` and `~review` behind the auth gate while their reading halves are owed now;
- the order, with `~overview` and `~design` already carrying [[TASK-0361]] and [[TASK-0362]];
- and why the other nine are **deliberately not task notes yet** — each would say *"port view X"* and nothing else, which is the thin-note proliferation [[ISS-0077]] warns about.

So *"both front doors"* is no longer a phrase quoted at pairs where only one side has the surface. It resolves to a stage: **owed now** (a read), or **behind [[REQ-0034]]** (a write). [[TASK-0511]]'s deferred picker is the second kind, and its note says so.

**What this issue does not claim.** The eleven views are not built. Nothing here ports a single one. What is fixed is the defect this note narrowed itself to — an obligation carried note-to-note *in a form nobody could discharge*, reading as an omission each time rather than as the precondition it was.

## Independent review — third pass, 2026-08-20

Fresh context, separate session, `model:claude-opus-5`, reviewing `6cc7f72..HEAD`. Verdict: **approved**. Every claim below was re-measured or re-executed.

Re-derived and correct on every point I could check.

- **`ADR-0010` is `accepted`, `decided_option: "4"`** — verified in `docs/decisions/ADR-0010-What-The-Browser-Cockpit-Is-For.md`. The self-correction is right.
- **The stage decomposition is faithful to option 4**, not read into it. Decision 4 says *"REQ-0034 is the unlock, and it gates PHASE-029"* (the auth write path is the gate); decisions 1–2 grant the Overview and the read-only Design register **now** (the reading views are ungated); decision 3 keeps every actuator mode-3 (the writing surfaces come after). Three stages, each with a sentence in the ADR behind it.
- **12 against 2 reproduces.** `cockpit.js` implements exactly `~note` and `~root`. `renderer.ts` matches 17 `~` routes, of which the note's 12 are the views; the other five (`~accept`, `~note`, `~root`, `~session`, `~sweep`) are addressing and sub-page routes. The curation is defensible but the note does not say it curated — worth one clause.
- **The four annotated notes are the right four.** `FEAT-0084`, `TASK-0364`, `TASK-0365` and `REQ-0032` are the live ones; annotating the 21 terminal records would have been the second-encoding defect this phase spent itself removing.

One hazard for a later reader: **there are two different `ADR-0010`s in the fleet** — this repo's *What the browser cockpit is for*, and `project-os-dev`'s *Test status is stamped by execution*. This note links `[[ADR-0010]]` unqualified. I resolved to the wrong one first.

## Independent review — fourth pass, 2026-08-20

Fresh context, separate session, `model:claude-opus-5`. Verdict: **changes-requested** (supersedes the third-pass verdict above). Re-measured or re-executed, not read.

Upgraded from my third-pass `approved` on one new finding. Everything I verified before still holds — `ADR-0010` accepted on option 4, the stage decomposition faithful, 12-against-2 exact, and the 11-owed / 1-gated split correct with `~release` gated because it composes contents.

**The third criterion's population count is wrong, and the rule it states is not the rule applied.** The note reasons: 25 notes carry *"both front doors"*, 21 are terminal records describing what was done, so only 4 are live and need a stage. Measured:

| | claimed | measured |
|---|---|---|
| notes carrying the phrase | 25 | **25** |
| terminal | 21 | **17** |
| live | 4 | **8** |

The eight live ones are `FEAT-0084` (planned), `TASK-0364`, `TASK-0365` (backlog), `REQ-0032` (draft) — the four annotated — plus `CHG-20260820-The-Suite-Is-The-Verdict` (active), `TST-0073` (active), `ISS-0240` (open) and this note itself (open).

The four chosen are defensible on a *narrower* test than the one stated — *is this a live obligation about parity* rather than *is this terminal* — and excluding this note is obviously right. But the note argues from terminality, and by that argument four notes were missed. Either state the narrower rule, or annotate the rest.
