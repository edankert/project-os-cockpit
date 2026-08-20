---
type: "[[issue]]"
id: ISS-0242
aliases: ["ISS-0242"]
title: "Two different groups are both called `Automated tests` in the tests view — one is a derived acceptance section, the other is every non-acceptance test note, and which one you get depends on the repo"
status: open
owner: user:edwin
created: 2026-08-20
updated: "2026-08-20"
source: ["user:edwin"]
severity: medium
component: cockpit
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[ISS-0241-The-Section-Head-Restates-Its-Own-Arithmetic]]", "[[ISS-0068-One-Item-One-Home]]", "[[ADR-0039-Three-Sections-Derived-Not-Filed]]", "[[ADR-0034-Three-Axes-Not-One-Word]]"]
tests: []
---

# One name, two populations, and the repo decides which

## Problem

Edwin, 2026-08-20: *"Why does automated tests look different in this project then on the your-trainer project?"*

Because they are **not the same group**. Two builders emit a group called `Automated tests`, and which one a reader sees depends on whether the open repo's acceptance suite happens to contain a check with a `command:`.

| | `project-os-cockpit` | `your-trainer` |
|---|---|---|
| group key | `automated` | `tier3` |
| built by | the section builder, over non-acceptance `TST-*` notes | `_acceptance_tier_groups` |
| what a row is | a test note | an **area surface** over acceptance checks |
| rows | 37 | 17 |
| what the count means | — (no count) | 89 acceptance checks |
| head | `Automated tests` | `Automated tests · 89` |
| `head_counts` | absent | `true` |
| links to | the test note | the generated checks page, filtered to the section |

Measured 2026-08-20 at HEAD. The sections present in each suite:

- `project-os-cockpit` — `feature: 27, regression: 7`. **No automated acceptance checks at all**, so `_acceptance_tier_groups` emits no `tier3` group and the name falls through to the unrelated one.
- `your-trainer` — `feature: 404, regression: 86, automated: 89`.

So the same two words mean *"the test notes a machine runs"* in one repo and *"the acceptance checks carrying a `command:`"* in the other, and nothing on either surface says which is on screen.

## Why it matters

This is [[ISS-0068]] — one item, two homes — turned inside out: **two items, one name**. It is worse than the original, because the collision is invisible in any single repo. Nobody comparing two repos side by side is comparing what they think they are, and the fleet surfaces are precisely where that comparison happens.

It also defeats the thing [[ADR-0039]] built. A derived section is supposed to be an answer to *what is this check for* — `command:` and `covers:`, nothing filed. A group that appears under the same name whether or not any such section exists makes the derivation unobservable.

## Expected

Two names, or one group. Not yet decided — this is the question, and the options are genuinely different:

1. **Rename the non-acceptance group.** It holds feature-scoped and system `TST-*` notes that are not acceptance checks; `Automated tests` was never a precise name for it. Cheapest, and leaves the derived sections owning the vocabulary [[ADR-0034]] gave them.
2. **Merge them.** An automated acceptance check and an automated test note are both *a thing a machine executes*; a reader may not care which schema it came from. But they are addressed differently, rendered differently, and only one of them gates a release — so a merged group would have to say which rows are which, and that is the distinction the merge was supposed to remove.
3. **Always emit the derived sections, empty ones included.** Makes the absence visible rather than silently substituting another group. Argues against [[REQ-0047]]'s landing state, which is deliberately not an inventory.

Option 1 is the recommendation. It is the only one that costs nothing if the answer later turns out to be 2.

## Evidence

`_tests_groups` on both repos, same commit:

```
project-os-cockpit   key=tier1  head_counts=True   'Feature tests · all 27 done · 1 reconciled'
                     key=tier2  head_counts=True   'Regression tests · all 7 done'
                     key=automated  head_counts=None   'Automated tests'          <- 37 test notes
                     key=retired    head_counts=None   'Retired · no longer verified'

your-trainer         key=needs-you  head_counts=None   'Needs you'
                     key=tier1  head_counts=True   'Feature tests · 45 of 406 outstanding'
                     key=tier2  head_counts=True   'Regression tests · 14 of 86 outstanding'
                     key=tier3  head_counts=True   'Automated tests · 89'         <- 17 area surfaces
                     key=retired    head_counts=None   'Retired · no longer verified'
```

## Next Actions

- [ ] Decide between the three options above; 1 is recommended.
- [ ] Whichever is chosen, a test that fails if two emitted groups share a label — the class, not this instance.
