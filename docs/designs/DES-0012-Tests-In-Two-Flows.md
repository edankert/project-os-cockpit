---
type: "[[design]]"
id: DES-0012
aliases: ["DES-0012"]
title: "Tests in two flows — how `TST-*` serves the development flow and the release flow, as one query at two zoom levels"
role: proposal
status: "proposed"
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

## The five decisions

Full options, trade-offs and a worked mock are in the artifact beside this note.

1. **D1 — what groups the list.** Tier extended to every test / **scope** (recommended) / level. If scope: what happens to the **83 checks that cover nothing**?
2. **D2 — which field means automated.** `command:` alone / both, named differently / retire `automation:` and express it as `covers:` links.
3. **D3 — whether tier survives.** Demoted to an attribute, or removed ([[ISS-0208]]). And the six never-walked Tier 3 checks: retire, or let them gate (60 → 66)?
4. **D4 — what a release contains.** Confirm the picker: features *and* phases, written to the note, **opt-in**, refusing on a frozen release.
5. **D5 — where a walk happens.** Does [[ADR-0035]] hold for a release-scoped *test list*? I lean to holding it.

## Consequences

- [[FEAT-0128]] is partly built against the old shape and will need revisiting under D1 — the collapse and the tracking line survive any answer; the grouping does not.
- [[FEAT-0129]] is unblocked by D4 alone and is the prerequisite for the release lens.
- The sweep ([[FEAT-0115]]) is the mechanism that *creates* `invalidated_by:` data. Both re-run populations are currently **0 in every repo**, so the tracking line has nothing to track until sweeps happen — which makes the sweep obligation load-bearing for this design rather than incidental to it.
