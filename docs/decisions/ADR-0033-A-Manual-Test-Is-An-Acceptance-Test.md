---
type: "[[adr]]"
id: ADR-0033
aliases: ["ADR-0033"]
title: "A manual test is an acceptance test — `kind: manual` outside `level: acceptance` is a contradiction, and the tier system already holds the case it was invented for"
status: superseded
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
decision_date: ""
phase: "[[PHASE-036-One-Human-Walk]]"
supersedes: ""
superseded: "[[ADR-0034-Three-Axes-Not-One-Word]]"
related: ["[[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]]", "[[ADR-0029-The-Acceptance-Mark-Vocabulary-Is-Minimals]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[ADR-0028-Work-Has-Three-Phases]]", "[[ISS-0195-Two-Types-Carry-One-Act]]", "[[TESTING-MODEL]]"]
tags: [testing, conventions, schema]
---

# A manual test is an acceptance test

## Status

**Superseded by [[ADR-0034-Three-Axes-Not-One-Word]] on the day it was proposed**, and the reason is worth more than the note. Its conclusion is right — a manual test is an acceptance test — and its *reason* was the wrong axis: it argued from re-arming, then wrote as an accepted cost that *"manual tests gate a feature and acceptance tests gate the release."* Edwin: *"It doesn't matter … they should be able to gate at any granularity."* That sentence was the conflation restated as a consequence. The migration this ADR asks for survives inside ADR-0034 as a **consequence** of separating the axes rather than as the decision itself.

**Proposed 2026-08-18.** Nothing changes type or status until Edwin accepts it — the gate [[ADR-0030]] and [[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]] both used, for the same reason.

## Context

[[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]] merged the `check` type into `test` and left **two human-walked populations inside one type**: acceptance tests at `level: acceptance`, and manual tests at every other level. The merge was defended on the ground that they are different things.

Edwin, 2026-08-18, having read the model note: *"Why would these manual tests not be true in a year? If the feature changes or code the feature is dependent upon changes, the test has to be re-run. I think a manual test is always an acceptance test and can be marked as complete/ticked or if changes happen can be unticked."*

**He is right, and the corpus says so in its own words.** The distinction offered for the two populations was that a manual test *verifies a change and retires*, while an acceptance test *names standing behaviour and re-arms*. The first half is fiction:

- `TST-0024` (Remote SSH walk) does not retire when FEAT-0099 ships. It re-arms the next time that code changes.
- `your-trainer`'s `TST-0018`, cited as the example of a test with a retirement path, says of the half that stays: **"which stays manual permanently."**
- Of 22 `kind: manual` tests fleet-wide, **zero** have ever reached a terminal status by being superseded by automation.

**And the case the split was invented for already has a home.** TESTING.md's **Tier 3** is *"one-time checks for a specific build, promoted to Tier 2 or removed after a verified release."* The one genuine verifies-this-build-then-stops-meaning-anything case — this repo's `TST-0026`, which asserts a measured "64 to 31" claim that would give different numbers on any later day — is a **Tier 3 acceptance test**, not a separate kind of note.

## The tell: two re-arming models for one act

| | manual test today | acceptance test today |
|---|---|---|
| re-arms by | **time** — `last_verified` against a 90-day threshold | **change** — `invalidated_by:` against `verdict_date:` |
| verdict in | `status: passing` | `mark:` |
| gates | a task/issue/feature reaching terminal | the release |
| on the badge | yes | never |

*"This walk was true 89 days ago"* is not the question anybody asks. *"Has anything changed underneath it"* is — and that is exactly what `invalidated_by:` answers. Time-based staleness is a proxy for change that a corpus with an invalidation field no longer needs.

## Decision

1. **`kind: manual` at any level other than `acceptance` is invalid.** A human-walked test *is* an acceptance test; the validator refuses the combination once the corpus is migrated.
2. **The 22 manual tests migrate to `level: acceptance` at a tier**, chosen per note: Tier 1 for a capability, Tier 2 for a regression guard naming its `ISS-*`, **Tier 3 for a one-build verification** — which is where the genuinely transient ones go, and which retires them after a verified release exactly as TESTING.md already describes.
3. **`Needs a run` disappears as a population**, and with it the `test` obligation's manual clause. What a person owes is what the tiers already say: unsettled Tier 1/2 rows. This is the second half of [[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]'s reasoning arriving where it always pointed.
4. **One predicate for "who runs this."** `cockpit._is_manual_test` reads `command:` first; `obligations._is_owed` has its own rule that never reads `command:` at all, and **8 of 788 fleet tests disagree between them**. The obligation's rule goes; the reader's stays.
5. **Time-based staleness is retired for human-walked tests** in favour of `invalidated_by:`. `last_verified:` remains as the date of the walk — which is what `verdict_date:` already is, so the two merge.

## Consequences

**This finishes what [[ADR-0031]] started.** That decision merged the types and left the two populations inside one; [[ISS-0195-Two-Types-Carry-One-Act]] measured the overlap from one end and Edwin found it from the other. The residue is small — 22 notes fleet-wide, 5 of them here — and the surface simplification is large: one population, one verdict field, one re-arming model, one verb.

**A known duplicate resolves by construction.** This repo's `TST-0011` item 7 is `TST-0065` *"The fleet view"* and `TST-0064` *"A session is visible while it runs"*. Once TST-0011 is a set of tiered checks, the same behaviour stops being verified twice by records that do not know about each other.

**What is lost, stated rather than discovered:** a manual test currently gates a *feature* reaching `done` through VERIFY, and an acceptance test gates only the release. Migrating them moves 22 notes out of the feature gate. That is the reverse of the direction [[ADR-0030]] worried about and it must be decided, not absorbed — either acceptance tests gain a feature-level gate through `covers:`, or those features are gated by their automated tests alone.

## Alternatives considered

- **Keep both and document the difference.** Rejected: the difference offered does not survive its own examples, and the cost of the ambiguity is measurable — the badge and the reader disagree about 8 notes, and the same behaviour is walked twice in this repo.
- **Make manual tests re-arm by change without moving them.** This fixes the sharpest symptom and leaves two verdict fields, two gates and two verbs for one act. It is the smaller change and it preserves exactly the confusion Edwin identified.
