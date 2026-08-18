---
type: "[[issue]]"
id: ISS-0202
aliases: ["ISS-0202"]
title: "A `draft` requirement keeps a manual test owed while the feature it verifies is `backlog` — and a check cannot be scoped to a release, so another platform's work blocks this one"
status: open
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
severity: medium
component: cockpit-server
phase: "[[PHASE-999-Future]]"
related: ["[[ADR-0028-Work-Has-Three-Phases]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[TESTING-MODEL]]", "[[ISS-0201-Walk-And-Run-Vocabulary]]"]
---

# What makes a test appear in `Needs a run` rather than under a tier

Edwin, 2026-08-18: *"On this project there is one item identified as needing a run but the feature/phase is not in-flight. On the your-trainer project there are some items which need a run which are not part of this release … What makes an item appear in needs a run and not in the Tier1 / Tier 2 acceptance tests section?"*

## The direct answer

They are **different populations of the same type**, separated by `level:`:

- **`Needs a run`** holds tests that are **not** `level: acceptance`, are manual (no `command:`), and sit at `status: ready`. This repo has exactly one: `TST-0024`.
- **`Tier 1/2/3`** hold the `level: acceptance` population — 34 here, 579 in `your-trainer`. They never appear in `Needs a run`, by construction: they rest at `active` and the obligation is keyed on `ready`.

So nothing is in the wrong group. But both halves of Edwin's observation are real defects underneath that answer.

## Defect 1 — a `draft` requirement outvotes a `backlog` feature

`TST-0024` covers three subjects:

| subject | status | phase |
|---|---|---|
| FEAT-0099 | `backlog` | PHASE-033 (`planned`) |
| REQ-0035 | `draft` | PHASE-033 |
| REQ-0036 | `draft` | PHASE-033 |

`RESTING_STATES` contains `backlog` but **not `draft`**, and `ids_in_flight` is *"in flight if ANY subject is"*. So the two `draft` requirements make the test live even though the feature it verifies has not been started and its phase is `planned`.

**The ANY rule was written for peers** — *"a section naming several features … is walkable while one of them is live"*. Here the subjects are a feature **and its own requirements**, which are not peers: a `draft` requirement of a `backlog` feature is not independent evidence that anything is live. It is the same fact counted twice, in the direction that asks.

Asking somebody to hand-walk a remote-SSH procedure for a feature that does not exist is exactly the noise [[ADR-0028-Work-Has-Three-Phases]] exists to remove.

## Defect 2 — a check cannot belong to a release

`your-trainer`'s 60 blocking checks include iOS work that is not in the release being prepared. There is no field that says which release a check belongs to, so the gate treats one undifferentiated set: **platform-scoped work blocks a release that does not contain it.**

The suite has `platform:` on some notes and the nav supports a platform filter, but the *gate* does not read it, and a release's own record derives its feature list rather than its check list.

## What would settle it

- [ ] `ids_in_flight` should not let a subject's own requirement vote independently of the subject. The narrow fix is to treat `draft` as resting for a requirement whose implementing feature is itself resting; the broader one is to rank subjects rather than OR them.
- [ ] Decide how a check is scoped to a release — a field, or derived from `covers:` against the release's features — and make `blocking()` read it. Until then the gate's number answers a question nobody asked.

## Independent review

**2026-08-18, `model:claude-opus-5`, fresh context. Blast radius measured by rebuilding an `Index` over all twelve fleet repos and evaluating three candidate rules against `obligations._is_owed` + `ids_in_flight`, templates excluded.**

### Defect 1 — confirmed, and there is a sharper argument for it than the note makes

The table is exact: `FEAT-0099` `backlog`, `REQ-0035`/`REQ-0036` `draft`, all three in `PHASE-033` (`planned`); `RESTING_STATES = COMPLETED_STATUSES | {backlog, deferred}` and carries no `draft`; `ids_in_flight` returns on the first non-resting subject.

**The system already treats those same two requirements as resting — for their own obligation.** `REQ-0035` and `REQ-0036` each declare `implements: [[FEAT-0099]]`, so `subject_is_in_flight` suppresses their own `Approve`: the features landing payload lists `REQ-0032` and `REQ-0034` and not them. So at this moment the cockpit holds both positions about the same two notes — *resting* when asked about the requirement, *in flight* when asked about the test that covers it. That is not a missing rule, it is one rule applied at one depth and not the next, which is a stronger claim than "the ANY rule was written for peers" and is checkable on today's corpus.

### The narrowing is safe. The alternative offered beside it is not

| rule | owed fleet-wide | quieted | which |
|---|---|---|---|
| today | 43 | — | — |
| `draft` resting when the implementing feature rests (this note's narrow fix) | 42 | 1 | `TST-0024` |
| `RESTING_STATES ∪ {draft}` (the crude version) | 42 | 1 | `TST-0024` |
| rank subjects as ALL-must-be-live | 38 | 5 | `TST-0024`, your-health `TST-0012`/`TST-0013`, your-trainer `TST-0011`/`TST-0013` |

Two things follow. **The narrow fix costs exactly the note that motivated it** — one row, in this repo, moving from `Needs a run` to `Resting · no feature in flight`, where it can still be seen. And **the narrow and crude versions are indistinguishable on today's fleet**, so the argument for preferring the narrow one is about future corpora, not about avoiding present damage; say that rather than implying a measured difference.

**The "broader" option should be struck, not carried as an alternative.** Implemented as ALL-must-be-live it silences four tests whose subjects include a feature at `doing`: your-health `TST-0012` (`FEAT-0041` doing), `TST-0013` (`FEAT-0044` doing), your-trainer `TST-0011` (`FEAT-0085` doing), `TST-0013` (`FEAT-0099` doing, eight `done` siblings outvoting it). Those are exactly the rows the ANY clause was written to protect, and `your-trainer`'s iOS parity walk is the one somebody is most likely to owe this week. Presented as a spectrum, the note offers a 1-row fix and a 5-row fix of which 4 are wrong.

### Defect 2 — right conclusion, misattributed evidence

*"`your-trainer`'s 60 blocking checks include iOS work"* does not hold. **Zero of the 60 blocking rows** mention iOS, iPhone, iPad or Apple in name, area or text; the set is `Trainer Compatibility Verification` (20), `Monetization & Licensing` (13), Strava/route/compat-test remainders. And **no acceptance note in `your-trainer` carries `platform:` at all** — 1414 notes in that repo do, none of them in the suite — so *"the suite has `platform:` on some notes"* is false for the suite.

The items you saw are `TST-0012` (*iOS BLE hardening acceptance*) and `TST-0013` (*iOS parity acceptance*), both `platform: ios`, both in **`Needs a run`** — the same population as Defect 1, not the tiers. That changes the shape of this issue: the scoping field you say is missing **exists on the population that produced the symptom** and is simply not read by the obligation, while the population you attributed it to has no such field and no release membership either. Two different gaps, and the note merges them.

The residual claim — *no field scopes a check to a release, and a release's record derives its feature list rather than its check list* — is correct and unfalsified.

**Verdict: Defect 1 approved, with the alternative narrowed to one option; Defect 2 needs rewriting around `Needs a run` and `platform:`, keeping the release-membership gap as its own statement.**
