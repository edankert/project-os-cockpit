---
type: "[[design]]"
id: DES-0012
aliases: ["DES-0012"]
title: "Tests in two flows — how `TST-*` serves the development flow and the release flow, as one query at two zoom levels"
role: proposal
decided: 2026-08-18
status: "accepted"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
source: ["Edwin 2026-08-18, on the built surfaces: 'I want a clear design which clearly tells me how tsts should work together with the development flow and the release/deployment flow'"]
asset: "DES-0012-tests-in-two-flows.html"
implements: []
supersedes: ""
superseded_by: ""
related: ["[[ADR-0034-Three-Axes-Not-One-Word]]", "[[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]]", "[[ISS-0208-Retire-The-Tier-Rule]]", "[[ISS-0206-A-Check-Cannot-Belong-To-A-Release]]", "[[FEAT-0128-The-Tests-View-Leads-With-The-Work]]", "[[FEAT-0129-A-Release-Names-Its-Own-Contents]]"]
tags: [design]
---

# Tests in two flows

> **Written because the increments were wrong.** Edwin, on three delivered changes: *"Wow, it doesn't have anything I wanted."* Each one implemented a suggestion from my own list; none was checked against a design, because there was no design. This note is the missing artefact, and it is `proposed` — nothing else in [[PHASE-037]] should be built until D1 and D4 are answered.

## Problem

**The tests view is sorted three ways at once.** `_tests_groups` buckets non-acceptance tests by *verification state*; `_acceptance_tier_groups` buckets acceptance tests by *tier*, a statement about lifetime; nothing buckets by *what a test covers*, which is the only thing either flow asks about.

That is why `Needs a walk` sits outside the tier sections — not by choice, but because the two lists share no axis. Edwin: *"I wanted to see the needs a walk section to be folded in with the other tier tests."* Folding them is not a layout change; it is a decision about what a group **is**.

Measured 2026-08-18:

| repo | tests | acceptance | other | manual / auto | subjects covered |
| --- | --- | --- | --- | --- | --- |
| `your-trainer` | 600 | 579 | 21 | 19 / 2 | 80 of 102 features |
| `project-os-cockpit` | 77 | 34 | 43 | 5 / 38 | 40 |
| `your-sudoku` | 69 | 56 | 13 | 13 / 0 | 18 |

The manual/automated ratio **inverts** between repos, which is why no default is safe and the distinction has to be shown rather than assumed.

## Approach

**Two flows, one population, different scopes.** The development flow asks *is this feature done?* — scope, one feature. The release flow asks *can we ship this set?* — scope, a set of features. Same tests; `covers:` is the join.

The primitive already exists: `Suite.blocking_for(subjects)` returns what holds a subject set, and `blocking()` is its `subjects=None` case. **The two flows are the same query at two zoom levels**, and no surface presents them that way.

So the proposal is to group by **scope**, with tier, level and execution demoted to row attributes and filter chips — and the landing state collapsed to the tier summary that exists today, so choosing a feature or a release is what expands it.

## The defect this surfaced

**`command:` and `automation:` both answer "manual or automated", and they disagree by construction.** `command:` asks whether *this note* has a runner. `automation:` asks whether the *thing the check describes* is already covered by automated tests living elsewhere.

`your-trainer` carries **22 `full`, 181 `partial`, 376 `manual`** — a populated, useful field that no list surfaces, sitting beside the field [[ADR-0034]] declared the single answer to the same question. Edwin asked for *a* distinction; there are two, and D2 picks.

## The five decisions — answered 2026-08-18

### D1 — group by **surface**, which is `area:`, inside tier

Edwin: *"can we scope them differently, based on where they sit in the application instead, the surface they are supposed to test, these are always application level tests?"*

**The field already exists and holds exactly that.** `area:` and `section:` are 1:1 (76 and 76 in `your-trainer`), and Tier 1's values are the application's surfaces: *Profile Management, Hardware Connectivity, Workout Execution, AI Workout Builder, Monetization & Licensing*. Not features, not scopes — surfaces.

**So grouping by feature is dropped.** Edwin is right that it is unlike the rest of the tool and that 80 groups is unusable. `area:` gives 25 groups in Tier 1 and is what a person means by *where in the app*.

**Areas do not span tiers** — 25 + 46 + 5 = 76 distinct, no overlap — so area is a *sub-division* of tier rather than an orthogonal axis. The structure is therefore **tier → surface → rows**, which is what the generated page had until [[TASK-0513]] flattened it a few hours before this was written. That flattening was mine and it was wrong: the request it answered was about the left pane's tier sections, and I applied it to the page's surface headings. It is reverted.

**One caveat, for Edwin.** Tier 2's `area:` values are not surfaces — they are individual past bugs (*Family License on Cold Start, HRM Mid-Workout Reconnect, ERG Target Power Sync*), 46 of them over 158 checks. Grouping Tier 2 by area gives ~3 checks per group. That is faithful to how Tier 2 is authored, and it is a data question rather than a display one.

### D2 — `command:` only

Decided by Edwin. `automation:` stops being read as an answer to *who runs this*.

**Its cost, stated:** `your-trainer`'s 22 `full` and 181 `partial` checks all read as manual, which is true of the *check* and silent about the coverage behind it. And 66 Tier 3 checks sit in an area literally called *"Moved from Tier 1 / Tier 2 — Fully Automated"* while carrying `automation: manual` — the field already disagrees with itself, which is the strongest argument for dropping it.

### D3 — tiers stay; the names are `your-trainer`'s own, and Tier 3's lifecycle is already written

Edwin: *"those are very strange names for these tiers … please re-review the reason we created these tiers."*

Re-read from source. `your-trainer/tools/instructions/TESTING.md` defines them, and the cockpit's `_TIER_LABELS` copies the names verbatim:

| tier | TESTING.md's name | created when | lifetime |
| --- | --- | --- | --- |
| 1 | Feature Tests (permanent) | a feature is first implemented | never removed |
| 2 | Regression Tests (permanent) | a bug fix lands; each references its `ISS-*` | never removed |
| 3 | Verification Tests (temporary) | a one-time check for a specific build | **promoted to Tier 2, or removed, after a verified release** |

**They name why a test was created, not what it tests** — which is exactly why they read oddly next to a surface. The corpus confirms each definition: Tier 1's areas are surfaces, Tier 2's are individual bugs, Tier 3's are one-offs.

**Tier 3 already has the different lifecycle Edwin asked about**, in as many words: after a verified release it is promoted or removed. It is never reopened. What has not happened is the *doing* of it — **66 of Tier 3's 74 checks are the "Unit test replacement" rule's holding pen**, moved there because unit tests cover them, with TESTING.md saying *"remove after the next release"*. They were not removed. That is the real Tier 3 finding, and it subsumes [[ISS-0208]]'s six unwalked rows: Tier 3 is not a gate question, it is a **housekeeping obligation nobody performs at release**.

### D4 — agreed, and platform enters it

Edwin: *"this is important now that we have iOS features and Android features/phases, each of them have their own releases (although going forward they probably have the same releases?)"*

The picker must therefore be **platform-aware**: `platform:` already exists on notes and the nav already filters by it. A release picks features, and the candidate list is narrowed by the release's platform. If iOS and Android converge on one release later, a release with no platform takes both — which is the same opt-in rule as contents.

### D5 — one verb, and it is not "walk"

Edwin: *"can you stop talking about 'walking'."*

Dropped, in the prose and in the product. [[TASK-0495]] changed the registry's verb from `Run` to `Walk` on the argument that a person walks a procedure and a machine runs a command. **D2 removes the premise**: with `command:` as the only answer to who runs a test, one verb covers both — a test with a command is run by a runner, one without is run by a person. `Run` comes back, and the guard that made `Walk` permanent gets inverted.

That is the second reversal of this verb in a week. It is worth recording that both were argued from the same fact and reached opposite conclusions, and the tie-break was that a reader should not need the argument.

## Consequences

- **[[TASK-0513]] is reverted**: the generated page returns to tier → surface → rows. Flattening it removed the exact structure D1 restores.
- **Progress is a bar, not a number.** Edwin: *"I want to see a bar the same as we do for phases on the overview page … this could nicely be per scope/surface."* `.ov-phase-under` and the segmented `.ov-mixbar` already exist; a surface group gets one, and so does each tier.
- [[FEAT-0128]]'s collapse and tracking line survive; its grouping does not.
- [[FEAT-0129]] is unblocked by D4 alone and is the prerequisite for the release lens.
- **Tier 3 needs a release-time obligation** — promote or remove — which is where its 66 overdue rows come from. New, and not yet scoped.
- The sweep ([[FEAT-0115]]) is the mechanism that *creates* `invalidated_by:` data. Both re-run populations are currently **0 in every repo**, so the tracking line has nothing to track until sweeps happen — which makes the sweep obligation load-bearing for this design rather than incidental to it.
