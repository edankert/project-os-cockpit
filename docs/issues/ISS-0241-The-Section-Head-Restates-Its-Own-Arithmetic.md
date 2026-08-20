---
type: "[[issue]]"
id: ISS-0241
aliases: ["ISS-0241"]
title: "The tests-view section head restates its own arithmetic, counts a different population beside it, and claims an execution nobody observed"
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
related: ["[[ISS-0222-The-Left-Pane-Groups-By-Tier-And-Nothing-Else]]", "[[ISS-0225-A-Nav-Row-Carries-Data-No-Renderer-Draws]]", "[[ISS-0228-The-Test-Id-Renders-Twice-On-A-Row]]", "[[ISS-0237-An-Automated-Check-Still-Blocks-The-Manual-Walk]]", "[[ISS-0209-The-Acceptance-Gate-Reaches-No-Fleet-Repo]]", "[[ADR-0039-A-Sections-Membership-Is-Derived]]"]
tests: []
---

# The section head says three things and two of them are noise

## Problem

Found by use, not by audit — Edwin, reading the left pane on `your-trainer`, 2026-08-20. The head of a tests-view section carries three separate count expressions, and only one of them answers a question anybody has.

```
Feature tests · 361/406 completed · 45 todo                    50 · 1 done
```

**One.** `45 todo` is `406 − 361`. It is the fraction beside it, subtracted, printed again. Nothing can make the two disagree, so the second one carries no information at any moment in its life.

**Two.** The trailing `50 · 1 done` counts a *different population*. The label counts **checks** (406); the trailing summary is `groupHeadSummary` counting the group's **nav rows**, which for an acceptance section are area surfaces (50). Two numbers, adjacent, both plausibly "how many tests are in here", differing by a factor of eight, and the reader has nothing on screen that says why.

**Three.** An automated section reads `Automated tests · 89 executed by CI`. That is a claim about who ran something, derived from nothing but the presence of a `command:` field. The cockpit never looks at a CI run.

> **Basis of every `your-trainer` figure in this note: its WORKING TREE on 2026-08-20, not `HEAD`.** Corrected after independent review, which caught the phase's own recorded lesson being repeated. The difference is not a rounding: at `HEAD` that repo has **581 items, 68 blocking, and ZERO command-bearing checks** — so there is **no automated section there at all**, and the 89 checks, their empty `evidence:`, the nine at `mark: todo` and the shared 22-character command prefix exist only in the 591-file working tree. Its Feature tests head reads `65 of 507 outstanding` at `HEAD` against `49 of 411` in the tree.
>
> **The findings do not depend on the basis; the numbers do.** A head that miscounts, a percentage over checks with no result, and a uniform glyph are defects of the code, reproducible on any corpus that has the shape. What the working tree supplies is the *scale*.

## Evidence

Measured 2026-08-20 in `your-trainer`'s **working tree** (not `HEAD` — see the basis note above), sidecar on 8801:

| head, as rendered | label counts | trailing summary counts |
|---|---|---|
| `Feature tests · 361/406 completed · 45 todo` | 406 checks | 50 rows |
| `Regression tests · 72/86 completed · 14 todo` | 86 checks | 28 rows |
| `Automated tests · 89 executed by CI` | 89 checks | 17 rows |

On the third row, of the 89 checks the head calls *executed by CI*:

- **89 of 89** carry `evidence: []` and `verdict_date: ""`. No result has ever been recorded for any of them.
- **9 of 89** are `mark: todo` — not done by a person or a machine. The head counts them as executed.
- **No workflow executes them as checks.** `.github/workflows/` in `your-trainer` contains no `run-tests.py` step. `android-tests.yml` does run `testDebugUnitTest` and `connectedDebugAndroidTest` on push/PR touching `android/**`, so the underlying JVM and instrumented tests genuinely run — but nothing maps those results back onto the notes, which is why all 89 sit at `status: active`.

So the phrase is true about the *tests* and false about the *checks*, and the surface shows checks.

## Why this is the mirror of ISS-0237

[[ISS-0237]] found automated checks inside a **blocking** count — the surface claiming a person owed work that no person does. The fix moved them to `N executed by CI`, which removed the false obligation and installed a false assurance in its place: a reader now sees 89 covered-and-green where the record holds no verdict at all.

Both are the same defect in [[PHASE-037]]'s terms — a surface answering a question its reader did not ask. The reader asks *what do I still owe*; the head answers *here is the inventory, and incidentally a machine has this in hand*.

## Expected

One count expression per head, stating what is **outstanding**, with the scale kept so the number can be read against something:

```
Feature tests · 45 of 406 outstanding
Regression tests · 14 of 86 outstanding
Automated tests · 89
```

and, where a section is finished, the finished form rather than a zero:

```
Feature tests · all 27 done · 1 reconciled
```

`outstanding` rather than `todo` on Edwin's call. `re-check`, `stale` and `reconciled` survive: each is a distinct fact, not the same fact restated.

The trailing row count is dropped **on heads whose label already carries counts**, which is exactly the sections `_acceptance_tier_groups` emits. Phase, feature and task groups keep theirs — there the trailing summary is the only count present, and removing it would leave a head that cannot say how big it is.

## Decisions taken here

- **The CI claim is dropped, not corrected.** Edwin chose the neutral wording over surfacing `89 automated · no recorded result`: the head is not the place to open the evidence question, and a second number to keep true is a second number that can go stale. The measurement above is the record of *why* the phrase went, and [[ISS-0209]] holds the substantive gap — the acceptance gate executes in no repo that owns a check, so nothing downstream of these 89 is proven by CI being green.
- **The section is already named `Automated tests`**, so the surviving head is `Automated tests · 89` rather than `Automated tests · 89 automated`. The word twice is what [[ISS-0089]] and [[ISS-0090]] removed from the group heads and the record card; it should not come back through this door.

## Next Actions

- [x] Label built in `_acceptance_tier_groups` (`cockpit.py`).
- [x] Trailing summary suppressed on count-bearing heads, both front doors (`cockpit.js`, `renderer.ts`).
- [x] Guard the redundancy directly: a test that fails if the head prints a number derivable from the others.

## Fixed

See [[CHG-20260820-The-Section-Head-Says-What-Is-Owed]]. Five guards in `tests/test_tests_view.py`, **each proved on a mutant** rather than asserted and trusted — this phase has now shipped three checks that could not fire, every one of them written while fixing the previous review, so a predicate here is not believed until the case that should fail it has been constructed and watched to fail:

| mutant | test that caught it |
|---|---|
| restore `{checked}/{total} completed · {unchecked} todo` | `..._prints_no_number_the_others_already_give`, `..._tracking_line...`, `..._finished_section...` |
| restore `{total} executed by CI` | `..._an_automated_head_claims_no_ci_execution` |
| drop `head_counts` from the payload | `..._a_count_bearing_head_suppresses_the_trailing_row_count` |
| drop the suppression from `cockpit.js` | `..._both_front_doors_read_head_counts` |

The suppression test also asserts the **negative** half — that a non-section group does *not* carry `head_counts` — because that is the half a later simplification flattens: the rule reads like "heads do not need trailing counts" right up until it removes the only count a phase group has.

## Independent review — 2026-08-20

Fresh-context pass, separate session, `model:claude-opus-5`. Started from the notes and the diff `222e19e..6cc7f72`; the author's reasoning trace was not available to it. Verdict: **changes-requested**.

The arithmetic argument is correct and every server-side guard fires: mutants restoring `{checked}/{total} completed · {unchecked} todo`, restoring `executed by CI`, and dropping `head_counts` were each executed and each failed the named test.

**One guard cannot detect what it names.** `test_both_front_doors_read_head_counts` asserts only `"head_counts" in src`. In `desktop/src/renderer/renderer.ts` that token also appears in the `NavGroupData` interface and its JSDoc, so deleting the behaviour — `if (group.head_counts) summaryText = '';` — leaves the test green. Executed: 2 passed. The full suite failed only `test_desktop_build_is_not_stale`, which compares `dist/.source-hash` against the sources and therefore fires on *any* byte change to `renderer.ts` and passes again after `npm run build`. It is a build-freshness check, not a behaviour guard. The `cockpit.js` half is genuinely guarded — deleting its one line removes the only occurrence and the test fails (executed).

**Shared finding — every `at HEAD` measurement in this range is a working-tree measurement.** `your-trainer` carries 591 dirty files under `docs/`. Re-measured against a `git archive HEAD` and a fresh `--shared` clone: tier1 total **496** (not 406), tier2 **85** (not 86), and **zero** command-bearing acceptance checks — so at HEAD that repo emits *no automated section at all* and the 89/9-todo/`evidence: []` population does not exist there. The gate is **68** blocking at HEAD (43 covering a `FEAT`, ten features, 40 out of scope), not 59/39/nine/36. Every figure quoted reproduces exactly against the working tree. No note in this range carries a basis caveat, while `CHG-20260820-The-Suite-Is-The-Verdict` — the note six prior review rounds spent on this exact point — carries 24.

## Independent review — second pass, 2026-08-20

**This supersedes the first-pass verdict above. Current verdict: approved.** Same reviewer, same conditions — fresh context, separate session, `model:claude-opus-5` — re-run against the working tree after the first pass's findings were acted on. Every claim below was re-measured or re-executed rather than read.

The guard hole is closed and verified: deleting `if (group.head_counts) summaryText = '';` from the desktop renderer now fails `test_both_front_doors_read_head_counts` (executed). The basis blockquote's numbers are exact.

Two residues, neither blocking:

- **The new guard fails on a pure reformat.** Rewriting the suppression as `if (group.head_counts) {\n  summaryText = '';\n}` — behaviour identical — fails the test (executed). A guard that goes red on formatting is the kind that gets loosened; the sibling `test_the_gate_row_id_is_typed_like_a_feature_row` was rewritten in this very diff for exactly that reason.
- Line 43 still reads *"Measured 2026-08-20 against `your-trainer` at HEAD"*, which the blockquote above it contradicts. Correcting the sentence is better than disclaiming it.
