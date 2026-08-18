---
type: "[[adr]]"
id: ADR-0034
aliases: ["ADR-0034"]
title: "Three axes, not one word — `level` says what a test exercises, `command:` says who runs it, `covers:` says what it gates, and no axis implies another"
status: accepted
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
decision_date: 2026-08-18
phase: "[[PHASE-036-One-Human-Walk]]"
supersedes: "[[ADR-0033-A-Manual-Test-Is-An-Acceptance-Test]]"
superseded: ""
related: ["[[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]]", "[[ADR-0032-The-Verification-Link-Has-One-Direction]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[ADR-0029-The-Acceptance-Mark-Vocabulary-Is-Minimals]]", "[[ISS-0200-Marks-Versus-Statuses]]", "[[TESTING-MODEL]]"]
tags: [testing, conventions, schema]
---

# Three axes, not one word

## Status

**Accepted 2026-08-18.** Edwin's instruction is the acceptance: *"Implement, test and independently verify phase 036 and fix ISS-0200 as part of this, replace the characters with their status options."* Given against a phase note, three features and a measured precondition — the same gate [[ADR-0030]], [[ADR-0031]] and [[ADR-0033]] all used.

**And it decides [[ISS-0200-Marks-Versus-Statuses]] with it**, which this ADR had deliberately left open. That is Edwin's call to make in one pass rather than mine to keep separate: the corpus is being rewritten once, and the argument for holding the vocabulary back was to stop it being folded in *silently*, not to stop it being decided. It **supersedes [[ADR-0033-A-Manual-Test-Is-An-Acceptance-Test]]**, which was proposed six hours earlier and is right about its conclusion and wrong about its reason — see *Why this supersedes ADR-0033* below.

## Context

Edwin, 2026-08-18: *"Manual tests are not different to acceptance tests or other tests, they should be able to gate at any granularity. I think we don't need necessarily acceptance tests any more in that case?"* — and, on [[ADR-0033]]'s statement that manual tests gate a feature while acceptance tests gate only the release: *"It doesn't matter."*

He is right, and **two independent bodies of practice say the same thing.**

**ISTQB separates these axes deliberately.** A *test level* — component, integration, system, acceptance — describes the point in development. A *test type* describes the quality characteristic. The standard keeps them independent expressly to prevent gaps in a test concept, and **manual versus automated is neither**: it is an execution concern, held out of the core syllabus on purpose. Acceptance testing is defined by *whose criteria are being checked* (UAT, contractual, regulatory, alpha/beta) — never by who performs it.

**The Agile Testing Quadrants say it from the other direction.** Marick's axes, as Crispin and Gregory developed them, are *business-facing vs technology-facing* and *supporting the team vs critiquing the product*. **Manual/automated is not an axis.** Q2 — business-facing tests that guide development — is the ATDD/BDD quadrant and is routinely automated; Q3 is human by nature. So *business-facing* and *manual* are two claims, and this project has been making one word carry both.

## The conflation, precisely

`level: acceptance` currently implies **three** independent things at once:

1. a person walks it,
2. its verdict is `mark:` rather than a status,
3. it gates the release and nothing else.

Not one of those follows from what the word means.

## Decision

**Three axes, and no axis implies another.**

| axis | field | determines | determines nothing about |
|---|---|---|---|
| **what it exercises** | `level:` — `unit … acceptance` (ISTQB) | scope, and how a reader groups it | who runs it; what it gates |
| **who runs it** | `command:` present or absent | how the result arrives (exit code vs a person's verdict) **and how it re-arms** | what it exercises; what it gates |
| **what it verifies** | `covers:` | **what it gates, at any granularity** | who runs it; what it exercises |

1. **Gating is derived from `covers:` and from nothing else.** One rule: *an item may not reach a terminal status while a test covering it is unsettled.* A task, an issue, a requirement, a feature and a release are all "items"; a release gates on the union of what its contents cover. Granularity stops being a property of the test — which is Edwin's whole point, and it is not new mechanism: [[ADR-0032-The-Verification-Link-Has-One-Direction]] already built the link and only the release gate reads it.
2. **Re-arming is a property of execution, not of level.** A machine re-runs on every commit, so currency is free. A person does not, so *"has something changed under this walk"* has to be recorded — `invalidated_by:`. It attaches to **any test with no `command:`**, at any level, and the 90-day staleness threshold is retired for that population.
3. **`level: acceptance` survives and stops meaning anything else.** It is ISTQB-standard and it names something real; it will no longer imply manual, `mark:`, or release-scoped gating. Automating an acceptance test does not stop it being one.
4. **`kind: manual` is deleted as a field.** `command:` already answers it, and two fields answering one question is how the reader and the registry came to disagree about 8 of 788 tests.
5. **One outcome vocabulary for every test, written as words** (Edwin, 2026-08-18):

   | was | becomes | means |
   |---|---|---|
   | `x` | **`done`** | walked and it held |
   | `/` | **`incomplete`** | partially holds; the reason says which part |
   | `-` | **`canceled`** | will not be walked, and is not holding the release |
   | `!` | **`important`** | walked and failed, with the failure tracked |
   | `?` | **`question`** | walked and not understood — the check itself is unclear |
   | `" "` | **`todo`** | nobody has walked it |
   | *(new)* | **`rerun`** | it was walked, and a change since invalidated the result |

   **`rerun` is the addition and it earns the migration on its own.** Today an invalidated check is written as `mark: " "` plus an `invalidated_by:` block — *"nobody has walked it"* recorded against a check somebody walked. The two states were indistinguishable in the one field every surface reads, which is why `Stale evidence` had to be computed by comparing dates. As a value it is simply true.

   The characters were adopted because [[ADR-0029-The-Acceptance-Mark-Vocabulary-Is-Minimals]] found an existing convention rather than inventing one, and because the suite was a Markdown document where Obsidian rendered them. **The second reason died with the document**; the first is honoured by keeping Minimal's *distinctions* and dropping its *notation*, which was never the part carrying meaning in frontmatter.
6. **Tiers become lifetime, or they go.** Tier 1 (permanent capability), Tier 2 (permanent regression guard), Tier 3 (one build, then promoted or removed) is not a level and not a scope — it is *how long this test is expected to live*. Once gating comes from `covers:`, Tier 1/2/3 stops being load-bearing and survives only if it earns its place as a lifetime field.

## Why this supersedes ADR-0033

[[ADR-0033-A-Manual-Test-Is-An-Acceptance-Test]] concluded that a manual test is an acceptance test, and it got there by arguing that manual tests **re-arm rather than retire** — true, and the wrong axis. Its own decision then wrote *"manual tests gate a feature and acceptance tests gate the release, so migrating moves 22 notes out of the feature gate"* as an accepted cost. **That sentence is the conflation restated as a consequence**, and Edwin rejected it correctly: gating is not a property of the kind of test.

ADR-0033's migration is still needed — the 22 notes still move — but as a *consequence* of the axes being separated, not as the decision itself.

## Consequences

**A precondition, measured before deciding rather than found later: 83 of 669 acceptance tests have an empty `covers:` — 12%.** Under a covers-derived gate those 83 gate nothing and leave the release silently. The current tier rule has no such hole. So the order is forced: **backfill `covers:`, prove the derived gate reproduces the tier gate exactly, then retire the tier rule.** A gate that gets quieter during a migration is the one failure this project cannot afford twice.

**ADR-0027 is untouched and gets harder.** Per-check obligations stay forbidden. With gating uniform, the thing that keeps 669 rows off a badge is aggregation — *"60 unwalked checks stand between this release and shipping"*, one row — plus [[ADR-0028]]'s in-flight rule. Neither is new; both must be explicit rather than incidental.

**This is the third schema change to the same corpus in three weeks** ([[ADR-0030]], [[ADR-0031]], this). That is not an argument against being right, and it is an argument for landing it once, with the 83 already measured.

## Alternatives considered

- **[[ADR-0033]] as written** — collapse the manual population and keep release-scoped gating. Rejected: it fixes the population and leaves the conflation, so the next reader still cannot say why an acceptance test may not gate a feature.
- **Keep the tier rule as the gate and add `covers:`-derived gating alongside it.** Two gates over one corpus, disagreeing whenever `covers:` is thin — which is exactly the 83. Rejected for the reason [[ADR-0032]] gives about the verification link: two encodings of one fact drift, and the drift is silent.
- **Delete `level: acceptance` entirely**, as Edwin floated. Rejected on the research: it is a standard level with a real meaning, and removing it would lose the ability to say *this checks fitness for purpose* — which is the one thing the label should have meant all along.
