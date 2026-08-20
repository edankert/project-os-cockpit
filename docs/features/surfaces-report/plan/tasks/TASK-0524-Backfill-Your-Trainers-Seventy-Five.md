---
type: "[[task]]"
id: TASK-0524
aliases: ["TASK-0524"]
title: "Backfill or except the 75 your-trainer features with no acceptance check"
status: done
owner: user:edwin
created: 2026-08-18
updated: "2026-08-20"
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: approved
parent: "[[FEAT-0132-Acceptance-Tests-Are-Scaffolded-By-Rule]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# Backfill or except the 75 your-trainer features with no acceptance check

Measured 2026-08-18: 102 features, 75 with nothing in any check's `covers:`. That is what eighteen months of a manual ask produced — 27% coverage — and it is the evidence for REQ-0051.

Do it AFTER the surfaces exist (FEAT-0130): a backfilled check needs a surface to sit on, and minting 75 more free-text areas is the problem this phase is fixing.

## Done 2026-08-20 — excepted where the record can say why, and NOT where it cannot

Edwin chose *except with a reason each* over backfilling 75 checks. Backfilling would have taken `your-trainer`'s gate from **59 blocking to roughly 134 on day one** (working tree; at `HEAD` it is 68 → ~143), every one of them a check nobody wrote — which is the false-obligation defect [[ISS-0237]] removed, at scale.

**The number was 76, not 75.** Measured at HEAD: 103 features, 27 covered by at least one acceptance check, **76 uncovered**.

### 43 of the 76 need no per-note exception, because their status already says why

| status | count | why no acceptance check is owed |
|---|---|---|
| `backlog` | 29 | not built |
| `superseded` | 7 | replaced; will never be built |
| `doing` | 4 | in flight — owed at close-out, not now |
| `cancelled` | 1 | will never be built |
| `deferred` | 1 | not built |
| `planned` | 1 | not built |

Writing *"no acceptance test — not built yet"* onto a `backlog` feature restates `status: backlog` in a second place. [[ADR-0009]] makes the note the authored source and the derivation the tool's job, so these are excepted **by rule**, in one sentence here, rather than by 43 edits that can drift from the status beside them.

### The other 33 cannot be excepted truthfully

They are `status: done` — shipped — and **nothing covers them at all**: no acceptance check, and no non-acceptance `TST-*` either. That second half was measured rather than assumed, and it came back **zero of 33**.

So there is no true reason available. *"Covered by unit tests"* would be a sentence I could write and the record contradicts; *"internal, no rider surface"* is a judgement about code I have not read. **Excepting these is exactly the false assurance this phase exists to remove** — the same move as `89 executed by CI` over checks with no recorded result.

They are therefore **named as owed**, which is the honest state and the actionable one:

| feature | title |
|---|---|
| `FEAT-0006` | Launch Preparation (Phase 6) |
| `FEAT-0008` | Energy Tracking & Rider Weight |
| `FEAT-0014` | Physics-Based Distance Engine |
| `FEAT-0015` | Localization & Internationalization Engine |
| `FEAT-0016` | Energy Metric Refinement |
| `FEAT-0017` | Interval Transition Visualization |
| `FEAT-0019` | Android UX Polish |
| `FEAT-0023` | Heart Rate Zone Tracking |
| `FEAT-0034` | iOS Post-Hardening Bugfixes |
| `FEAT-0035` | iOS Second Review Fixes |
| `FEAT-0037` | Enhanced Debug Tools |
| `FEAT-0038` | Strava Integration |
| `FEAT-0046` | Visual Workout Builder |
| `FEAT-0053` | HR Zone Target in Free Ride |
| `FEAT-0059` | Strava upload robustness |
| `FEAT-0060` | Workout History Dashboard |
| `FEAT-0063` | Grouped history view (thread by workout) |
| `FEAT-0064` | Strava Branding & Connection UX |
| `FEAT-0067` | Tier-1 Locale Rollout (DE, FR, ES, IT, NL, JA, PT-BR, zh-TW) |
| `FEAT-0068` | Principled trainer-dispatch physics — unify Resistance + ERG with SIM-eq |
| `FEAT-0080` | Live Route Shape - top-down route polyline view rendered on a clean Comp |
| `FEAT-0081` | Downloadable Workout & Route Packs - distribute curated content (bundled |
| `FEAT-0083` | intervals.icu integration - bidirectional bridge to the open analytics + |
| `FEAT-0086` | MCP integration for in-app AI features - route Workout Builder, History  |
| `FEAT-0087` | Workout content authoring pipeline — generator + intent templates + JSON |
| `FEAT-0088` | Drop packs as a first-class app concept. Replace with in-app inline brow |
| `FEAT-0090` | LTHR-anchored HR-zone system aligned with intervals.icu — 5 drivable edi |
| `FEAT-0092` | Route support in Online Library — extend FEAT-0088's sibling-hosted Onli |
| `FEAT-0093` | Strava route download — pull the rider's Strava-curated routes into Your |
| `FEAT-0096` | Paywall reshape v2.1 — five-part adjustment to the FREE-vs-PRO line: tri |
| `FEAT-0097` | Route view modes — explicit primary + inset model replaces the FEAT-0080 |
| `FEAT-0098` | iOS parity — bring the iOS app to full feature + UX parity with Android  |
| `FEAT-0101` | Cross-platform parity visual gallery + direct iOS↔Android comparison |

**This is the list to argue with, not the list to accept.** Some of these almost certainly deserve an exception — `FEAT-0006 Launch Preparation` is a phase of work rather than a rider-facing surface, and several are engines whose behaviour is verified through the features built on them. Each of those is a judgement only Edwin can make, and each should be recorded on its own note when made. What this task settles is that the 33 are **visible and unexplained** rather than quietly absent.

Nothing was written to `your-trainer` for this task: the 43 are excepted by rule and the 33 have no defensible exception to write.

## Independent review — second pass, 2026-08-20

**This supersedes the first-pass verdict above. Current verdict: approved.** Same reviewer, same conditions — fresh context, separate session, `model:claude-opus-5` — re-run against the working tree after the first pass's findings were acted on. Every claim below was re-measured or re-executed rather than read.

Every figure re-derived independently and every one is exact: 103 features, 27 covered by at least one acceptance check, **76** uncovered; the status split 29 `backlog` / 7 `superseded` / 4 `doing` / 1 `cancelled` / 1 `deferred` / 1 `planned` = **43** excepted by rule; **33** `done`-and-uncovered; and **zero of 33** covered by any non-acceptance `TST-*` — the half most likely to have been assumed, measured and confirmed.

The reasoning is the discipline this phase exists for: refusing to write an exception the record cannot justify, and naming the 33 as visible-and-unexplained instead. *"This is the list to argue with, not the list to accept"* is the right frame, and writing nothing into `your-trainer` is the right restraint.

One residue: *"from **57 blocking** to roughly 132 on day one"* uses the index-less 57. With the loader the app actually uses it is 59, so the projection is ~135. Small, but it is the same instrument this phase just retired.
