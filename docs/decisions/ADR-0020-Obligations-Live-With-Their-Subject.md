---
type: "[[adr]]"
id: ADR-0020
aliases: ["ADR-0020"]
title: "Obligations live with their subject — the review desk dissolves into the views, the count moves to the buttons, and Tests becomes a view"
status: "accepted"
owner: user:edwin
created: 2026-08-10
updated: "2026-08-10"
source: ["Edwin 2026-08-10, reviewing the view set: 'I don't think we need the separate review item then anymore ???'", "Session 2026-08-08..10: every nav mode and the desk payload measured against the corpus and the fleet"]
related: ["[[ADR-0007-Planning-Artifact-Approval-Gate]]", "[[DES-0005-The-Actuator-Grammar]]", "[[DES-0006-The-Acceptance-Desk]]", "[[DES-0010-The-Desk-Shows-What-It-Owes]]", "[[FEAT-0041-Review-Desk]]", "[[FEAT-0049-Review-Desk-As-Record]]", "[[FEAT-0061-Quick-Capture-And-Triage]]", "[[FEAT-0082-The-Desk-Shows-What-It-Owes]]", "[[ISS-0068-Waiting-On-You-Is-A-Workaround]]", "[[ISS-0121-Reviewed-Register-Counts-Settled-Work-As-Owed]]"]
reviewed_by: "user:edwin"
review_date: "2026-08-10"
review_verdict: "plan-accepted"
---

# Obligations live with their subject

## Why this ID and not ADR-0011

`counters.ADR` stood at 10, so the next local ID was 0011. **`ADR-0011` is referenced in 26 files in this repo and `ADR-0013` in 22**, every one of them meaning an *upstream* project-os decision — the independent-review deadline that every validator `[REVIEW]` warning cites, and the review-independence rule quoted in `CLAUDE.md` and `QUALITY.md`. No note with either ID exists locally or upstream.

Allocating 0011 locally would make twenty-six existing references ambiguous. So this takes 0020, safely above the whole referenced range (0011–0018). Counters only rise and an ID is allocated rather than owned, so skipping costs nothing; 0011–0019 are deliberately never used locally. **That the upstream ADR namespace is quoted here but absent is a real defect** — it is not this decision's to fix, and it should be filed.

## Context

The review desk ([[FEAT-0041]], [[ADR-0007]]) was built on the premise that obligations should land in one place. It now carries four queue groups (decisions, proposals, questions, test runs) and two registers (tests, reviewed), and [[DES-0010]] proposed widening it further into a board.

Three claims held it up. Measurement over 2026-08-08..10 retired two of them.

**"Questions can only live on the desk."** A question is ledger state with no note, so no view could host it. True — and irrelevant: **zero questions have ever been created.** The store holds 8 ledger requests across the repo's history, all of kind `review`. The argument defended an unexercised surface.

**"Only one surface can answer *am I done?*"** True of a *count*; false of a *page*. A per-view badge answers it without a visit, and answers it continuously rather than when asked.

**"A second desk splits the queue"** ([[DES-0006]]). Still true, and this decision does not create a second desk. It removes the first.

Meanwhile the desk had drifted in both directions:

- **It holds things that are not obligations.** `Tests · 23/23` is a browsable list of what gets verified; `Reviewed · 103` is a record of verdicts already given. Neither is owed.
- **It omits the largest obligation there is.** `QUEUE_INTAKE_STATES` deliberately excludes `issue: triage`. Measured across the fleet: **39 issues at `triage`, median age 56 days, 23 older than 30 days, oldest 114.** The desk reported `3 owed` for this repo while two triage issues went uncounted — a count that is wrong is worse than no count, and it was already wrong.
- **And what it did report was mostly false.** All ten `Changes requested` rows are terminal ([[ISS-0121]]).

The judgments themselves are not uniform, either. [[DES-0006]] already concluded that acceptance needs a guided walk rather than a queue row; triaging an issue wants the severity buckets it would join; approving a requirement wants the feature it specifies. The desk's uniform row was a shape imposed on unlike things.

## Decision

1. **An obligation surfaces in the view that owns its subject.** Designs and ADRs in Design; requirement approval and acceptance in Features; triage in Issues; test runs in Tests.
2. **The actuator stays on the note.** [[DES-0005]] is unchanged and unweakened: the view says something is owed, the note is where the judgment is made, and the server decides which transitions are legal ([[REQ-0026]]).
3. **The count lives on the view button**, and the set of badges must cover **every** obligation kind. A badge that omits a kind is the defect this decision exists to remove, not a simplification.
4. **Tests becomes a first-class view** — the register, the manual runner, the tier suite and the release gate. This is the one part that is new capability rather than re-homing: the acceptance contract in `TESTING.md` (Tier 1/2/3, "a release is blocked while any Tier 1/2 test is unchecked") has **never been instantiated** in this repo — 85 features, 23 test notes, zero tier classification, a gate that has never been able to fire.
5. **The review desk is retired**, its parts re-homed as below.
6. **Questions are dropped deliberately.** The ledger mechanism stays; no surface is built for a kind that has never occurred. If one occurs, [[FEAT-0062]] decides where it goes — as a decision, not a discovery.
7. **A record is not an obligation.** The reviewed register joins the record surfaces (where ADRs, changes and designs already are), not a queue.

### Where each part goes

| desk element | new home |
|---|---|
| Decisions — ADR `proposed` | Design |
| Proposals — requirement `draft` | Features |
| Proposals — design `proposed` / offered | Design |
| Test runs — manual `ready`, and the stepper | Tests |
| Tests register | Tests |
| `changes-requested` re-review | the view owning each note's type |
| "am I done" count | badges on the view buttons |
| Reviewed register | the record surfaces |
| Questions | nowhere, deliberately |

## Amendment 2026-08-10 — where changes live

Edwin, on reading this: *"Where do we capture/surface changes now?"* The re-homing table says `changes-requested` re-review goes to "the view owning each note's type", and **no view owns `change`**. The table was written from the desk's contents and `change` was never on the desk, so the gap was invisible from where it was drawn.

It is not a small omission. There are **116 CHG notes** — the third-largest type in the corpus — and **76 of them carry no `review_verdict`**. `change` is a `GATE_BEARING_TYPE`: those 76 are the `[REVIEW]` warnings the validator already emits, and they become **errors on 2026-10-23**. So changes carry the largest single pool of owed judgment in this repo, and this decision did not house it.

**Amended:**

8. **The Overview owns changes.** It already does — the history band ([[FEAT-0052]]) and the record column render them — and a change note is a record of what happened, which is what that surface is for. Nesting them under features was considered and rejected: a CHG frequently spans several items and many document process or docs rather than a feature, so the edge does not exist for all of them.
9. **Unreviewed changes are an obligation and get the Overview's badge.** By decision 3 the badges must cover every kind, and this is a kind.

**Left open, deliberately:** whether *historical* unreviewed changes are an obligation or an accepted state. Most of the 76 date to the repo's first weeks (`CHG-20260507-*`), and a badge reading `76` may drown the four kinds that are actionable today. A cutoff date, a waiver, or simply accepting the number are all defensible; the deadline makes it a real decision rather than a display preference, and it should be taken with the count in front of you rather than guessed at here.

## Amendment 2026-08-10 (second) — where releases live

Edwin, on reading the scaffolded plan: *"Where do the REL notes live in this new design?"* The same omission as changes, from the same cause: the re-homing table was drawn from the desk's contents, and a release was never on the desk, so it was invisible from where the table was written. This decision names the release *gate* (decision 4, as something Tests owns) and never says where a **REL note** goes.

It is no longer hypothetical — [[REL-0001]] was written today, ending six months of `counters.REL: 0`.

**Amended:**

10. **The Overview owns the release record**, on exactly the reasoning of amendment 8: a REL note is a record of what happened, at a coarser grain than a change note, and the Overview is the surface for that. This matches [[FEAT-0072]], which already puts `UNRELEASED · N` — features `done` since the last REL — in the overview's record column.
11. **Tests owns the gate.** *"A release is blocked while any Tier 1/2 test is unchecked"* is an obligation whose subject is a **test**, so by decision 1 it surfaces in Tests and is counted in its badge. The Overview says a release is owed; Tests says why it cannot ship.
12. **The gate band renders on the REL note itself**, like any note's own content. That is a rendering question, not a view-ownership one, and needs no rule.

**A conflict this surfaces.** [[FEAT-0072]] (PHASE-026) and [[FEAT-0086]] (PHASE-030) both claim the gate band on the release note — *"the REL note view surfaces the acceptance-tests template's own release gate"* against *"the release gate's surface — unchecked Tier 1/2 tests listed on a release note"*. Two features, two phases, one band. Under this amendment the band is **[[FEAT-0086]]'s**, because it owns the tier suite that makes the gate computable at all; [[FEAT-0072]] keeps the `UNRELEASED` card and the drafting action. Their notes should say so before either is built.

## What this does not change

**[[ADR-0007]] is narrowed, not reversed.** It decided that the approval gate is *advisory*, that acceptance stamps `reviewed_by`/`review_date`/`review_verdict` into the note, that rejection flips through a guarded transition, and that the queue is runtime state while the outcome is durable in the note. All of that survives; only the location of the queue changes. Its measurement clause — revisit gating once ~20 sets have passed — survives too, and is now measured from wherever the sets are shown.

**[[ISS-0068]]'s lesson is the constraint, not a casualty.** It removed the overview's *Waiting on you* because it re-listed items that already had a home elsewhere. The rule it established — **one home per obligation, marks elsewhere** — is exactly what this decision applies. Grouping an issue's triage state *within* Issues is regrouping items already in that view, as the existing `Open · 6` / `Completed · 4` split already does. What remains forbidden is a third surface listing them again.

**No write path widens.** Every actuator remains loopback-only, allow-listed and mtime-guarded ([[REQ-0027]]), and nothing here makes an agent-owned transition reachable.

## Consequences

**Superseded:** [[DES-0010]] and [[FEAT-0082]] design a board for a surface this retires. Nothing was built, so the cost is two notes; they take `superseded` with a pointer here rather than being deleted.

**Amended:** [[TASK-0284]]'s triage tray becomes the primary triage surface rather than a secondary one (and gains `Defer`, a legal transition it omits — with a median triage age of 56 days, "real, not now" is the most common honest verdict and today has nowhere to go). [[FEAT-0049]]'s registers move. [[DES-0006]]'s first entry point — "the desk queue gains *Awaiting your acceptance · N*" — becomes Features. [[DES-0005]]'s issue row needs its third verb.

**Unaffected:** [[ISS-0121]] is still a defect wherever the register renders.

**The cost, stated plainly:** discharging judgments becomes up to four visits instead of one. The badges make the four visible without visiting, and [[DES-0008]]'s landing digest (`since Thu · 14 transitions · 2 need you`) is where the single-pass workflow goes. If that proves insufficient in practice, the honest remedy is to strengthen the digest, not to rebuild the desk.

**What would falsify this.** If, after the views own their obligations, the triage pool still ages past ~30 days at the fleet median, then placement was not the constraint and the problem is attention, not architecture. That is measurable with the same script used here, and it should be re-run rather than argued about — the [[ADR-0006]] precedent.

## Alternatives rejected

- **Desk as index, views as context (both).** My own recommendation on 2026-08-09, before the questions measurement. It keeps two surfaces for one set of items, which is what [[ISS-0068]] warns about, and doubles the places a new obligation kind must be registered.
- **Desk only, no per-view surfaces.** Triage judged without the severity buckets it joins; and the desk would have to grow acceptance runs and the tier suite, becoming a second application beside the record it describes.
- **Per-view only, no count anywhere.** Loses "am I done", which is the desk's one irreplaceable property. Rejected — hence decision 3.
- **Deprecate obligations entirely and rely on the validator.** The validator sees rule violations, not owed judgments; a `draft` requirement is not an error.

## Open questions — deliberately not decided here

- **What the Design view is called** once it holds ADRs, risks, the brief and the glossary. "Design" is too narrow, and mode 1 already uses "Project" for `library`.
- ~~**Whether Library dissolves into it.**~~ **Answered 2026-08-10: it does not.** Edwin — *"I do want to keep the library view for now."* The split is by question: Library is a **file browser** (*where is that file*), the constraints view holds **typed notes** (*what constrains this project*). A `reference/` note therefore has two addresses, which is not the second-list failure [[ISS-0068]] describes. The boundary to watch is Library growing typed groups of the same notes; at that point they would genuinely duplicate.
- **Exactly which record surface takes the reviewed register.**
- **Whether requirements stay nested under features.** This decision assumes they do — a requirement constrains one feature and belongs beside it, while ADRs and risks constrain the project. Worth stating as an assumption because 32 notes turn on it.
