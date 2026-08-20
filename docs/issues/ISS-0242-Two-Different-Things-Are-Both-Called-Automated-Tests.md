---
type: "[[issue]]"
id: ISS-0242
aliases: ["ISS-0242"]
title: "Two different groups are both called `Automated tests` in the tests view — one is a derived acceptance section, the other is every non-acceptance test note, and which one you get depends on the repo"
status: fixed
owner: user:edwin
created: 2026-08-20
updated: "2026-08-20"
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: approved
source: ["user:edwin"]
severity: medium
component: cockpit
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[ISS-0241-The-Section-Head-Restates-Its-Own-Arithmetic]]", "[[ISS-0068-One-Item-One-Home]]", "[[ADR-0039-Three-Sections-Derived-Not-Filed]]", "[[ADR-0034-Three-Axes-Not-One-Word]]"]
tests: []
---

# One name, two populations, and the repo decides which

> **Basis of every `your-trainer` figure in this note: its WORKING TREE on 2026-08-20, not `HEAD`.** Corrected after independent review, which caught the phase's own recorded lesson being repeated. The difference is not a rounding: at `HEAD` that repo has **581 items, 68 blocking, and ZERO command-bearing checks** — so there is **no automated section there at all**, and the 89 checks, their empty `evidence:`, the nine at `mark: todo` and the shared 22-character command prefix exist only in the 591-file working tree. Its Feature tests head reads `65 of 507 outstanding` at `HEAD` against `49 of 411` in the tree.
>
> **The findings do not depend on the basis; the numbers do.** A head that miscounts, a percentage over checks with no result, and a uniform glyph are defects of the code, reproducible on any corpus that has the shape. What the working tree supplies is the *scale*.

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

Measured 2026-08-20 in the **working tree** (not `HEAD` — see the basis note above). The sections present in each suite:

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

## Corrected 2026-08-20 while implementing — the diagnosis above is wrong

**The two groups do not both render. They MERGE**, and I did not check before writing the table above.

`_SECTION_TO_TIER_KEY` maps `automated → tier3`, and `_tests_groups` appends the non-acceptance records into the tier host. So there is one group, and what differs is whether a host exists at all:

- **`your-trainer`** has 89 automated acceptance checks, so `tier3` is emitted and the non-acceptance rows are merged into it. Head: `Automated tests · 89`.
- **This repo** has none, so no `tier3` is built, the section falls through with a bare label, and its count is relegated to the trailing summary while every sibling carries one inline. Head: `Automated tests`.

That is the whole of *"why does it look different"* — **the same section, the same name, a different head, decided by whether the repo happens to hold a check of that kind.** Not two names for two populations.

### And the merge hid a worse defect, in every section

The head is built **before** the merge, so every row appended is invisible to it:

| section | checks the head counted | merged in, uncounted |
|---|---|---|
| `project-os-cockpit` Feature tests | 27 | 5 |
| `your-trainer` Feature tests | 406 | 5 |
| `your-trainer` Automated tests | 89 | 2 |

**The first row is what it cost.** This repo's head read `Feature tests · all 27 done` while three of its five merged rows sat at `ready`. A head asserting everything is finished, over a group holding three things that are not — [[ISS-0241]] arriving through a second door, and live on the surface until today.

## Fixed

- One `_section_head_label`, called again after the merge with the merged population. Heads now: `Feature tests · 3 of 32 outstanding · 1 reconciled` here, `49 of 411` and `Automated tests · 91` in `your-trainer`.
- A section with no acceptance checks gets the same head as one that has them — `Automated tests · 37` here. `Needs you`, `Broken command` and `Retired` deliberately keep their trailing summary: they are cross-cutting state groups, not sections of the suite.
- `_head` is popped before the payload is emitted, and a test asserts it, because a key the server sends and no renderer reads is [[ISS-0225]].

**The predicate took two attempts and the first one shipped a wrong number in this very fix.** Outstanding was first read off `progress.done`, which `_test_as_surface` derives from the row's `owed` flag — the obligations registry's question, *does this need a person right now* ([[ADR-0027]]) — which answers `False` for a test at `ready`. The head still printed `all 32 done`. It now asks `statuses.is_completed`, the narrower question the view is about, from the module where the bands are already canonical for six surfaces. Both readings are guarded: `test_a_ready_test_is_outstanding_not_done` fails on the `owed` version.

The fixture needed the same care. A `ready` test with a *live* obligation is routed to `Needs you` and never reaches the section — so the first fixtures asserted against a group the row was not in, and failed against `all 4 done` for a reason that had nothing to do with the bug. `_merged_test` gives the subject a terminal status so the in-flight rule quiets it, which is the corpus's actual shape.

## Next Actions

- [x] Decide between the three options — **overtaken**: the sections already merge, which is option 2, so the question was never live. What needed deciding was where the head's numbers come from.
- [x] The head counts what the section holds, merged rows included.
- [x] A section with no acceptance checks gets a section head.
- [x] Four guards, each proved on a mutant: zeroing the merged count, swapping `is_completed` back to `owed`, disabling the standalone head, and leaking `_head`.

## Independent review — 2026-08-20

Fresh-context pass, separate session, `model:claude-opus-5`. Started from the notes and the diff `222e19e..6cc7f72`; the author's reasoning trace was not available to it. Verdict: **changes-requested**.

The self-correction is the strongest thing here and it is right: the groups merge, and re-measurement confirms every post-fix head — `Feature tests · 3 of 32 outstanding · 1 reconciled`, `Automated tests · 37` in this repo; `49 of 411` and `Automated tests · 91` in `your-trainer`'s working tree (406+5, 89+2).

**`statuses.is_completed` is the right predicate and the reasoning holds.** `_test_as_surface` sets `progress.done = 0 if row['owed'] else 1`, and `owed` is quieted for a `ready` test whose subject is terminal — so the two genuinely differ on this repo's own three `ready` merged rows. Both counting sites read the same raw field (`_test_item` sets `"status": record.status`), so the standalone-head branch and the merge branch cannot disagree. The mutant swapping back to `progress.done` was executed and fails `test_a_ready_test_is_outstanding_not_done`.

**`_head` cannot leak by another path.** `_acceptance_tier_groups` has exactly one caller; every group in the return value passes through the pop; there is no early return. Measured `leaked=[]` on both corpora.

Two corrections: the `Evidence` table's `feature: 404, regression: 86, automated: 89` is `404`, measured `406`; and see the shared basis finding below — at HEAD `your-trainer` is `feature: 496, regression: 85, automated: none`.

**Shared finding — every `at HEAD` measurement in this range is a working-tree measurement.** `your-trainer` carries 591 dirty files under `docs/`. Re-measured against a `git archive HEAD` and a fresh `--shared` clone: tier1 total **496** (not 406), tier2 **85** (not 86), and **zero** command-bearing acceptance checks — so at HEAD that repo emits *no automated section at all* and the 89/9-todo/`evidence: []` population does not exist there. The gate is **68** blocking at HEAD (43 covering a `FEAT`, ten features, 40 out of scope), not 59/39/nine/36. Every figure quoted reproduces exactly against the working tree. No note in this range carries a basis caveat, while `CHG-20260820-The-Suite-Is-The-Verdict` — the note six prior review rounds spent on this exact point — carries 24.

## Independent review — second pass, 2026-08-20

**This supersedes the first-pass verdict above. Current verdict: approved.** Same reviewer, same conditions — fresh context, separate session, `model:claude-opus-5` — re-run against the working tree after the first pass's findings were acted on. Every claim below was re-measured or re-executed rather than read.

Basis blockquote present and accurate. The `Evidence` table's *"Measured 2026-08-20 at HEAD"* caption (line 44) is still uncorrected in place, but the blockquote above it now carries the true basis. No new defect found; the merge logic, the predicate choice and the `_head` pop all stood up to re-testing in the first pass and are unchanged.
