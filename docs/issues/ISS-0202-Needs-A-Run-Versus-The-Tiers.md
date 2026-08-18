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
