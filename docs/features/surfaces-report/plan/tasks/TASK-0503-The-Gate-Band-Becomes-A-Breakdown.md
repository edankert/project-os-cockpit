---
type: "[[task]]"
id: TASK-0503
aliases: ["TASK-0503"]
title: "Replace the sixty-row blocking wall with a breakdown by area, each part linking to a filtered `~checks`"
status: done
owner: user:edwin
created: 2026-08-18
updated: "2026-08-20"
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: changes-requested
parent: "[[FEAT-0125-The-Release-Page-Reports-What-Holds-It]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# Replace the sixty-row blocking wall with a breakdown by area, each part linking to a filtered `~checks`

The verdict line and confidence roll-up stay. `gate.blocking` carries `area` on every row, so the breakdown is a tally over data already in the payload.

Lossless: the full list stays reachable through the links, and the count in the heading must equal the number of rows behind them.

> **Basis of every `your-trainer` figure in this note: its WORKING TREE on 2026-08-20, not `HEAD`.** Corrected after independent review, which caught the phase's own recorded lesson being repeated. The difference is not a rounding: at `HEAD` that repo has **581 items, 68 blocking, and ZERO command-bearing checks** — so there is **no automated section there at all**, and the 89 checks, their empty `evidence:`, the nine at `mark: todo` and the shared 22-character command prefix exist only in the 591-file working tree. Its Feature tests head reads `65 of 507 outstanding` at `HEAD` against `49 of 411` in the tree.
>
> **The findings do not depend on the basis; the numbers do.** A head that miscounts, a percentage over checks with no result, and a uniform glyph are defects of the code, reproducible on any corpus that has the shape. What the working tree supplies is the *scale*.

## Done 2026-08-20

`gateAreaBreakdown` renders in front of the blocking list — never instead of it — on the groups that ask, and each part opens `~checks/area/<area>`.

**Measured before drawing it**, in `your-trainer`'s **working tree** (not `HEAD` — see the basis note above): **59 blocking rows across 17 areas**, and the shape is the reason the tally is worth the space — `Trainer Compatibility Verification` holds 20 and `Monetization & Licensing` 11, so two areas are more than half the gate. A 59-row scroll hides that; the tally is the first thing on the page that a person can act on.

**The filter is in the ADDRESS**, `~checks/area/<area>`, on [[ISS-0203]]'s rule: a filter that lives in a click cannot be linked to, cannot be reopened with back/forward, and does not survive a navigation. It is also assigned unconditionally, so a bare `~checks` clears it — the sticky-filter defect ISS-0203 removed from the tier axis.

**Lossless, and the guard is on the property that can break quietly.** `test_the_gate_breakdown_is_lossless_and_sums_to_its_list` fails if the tally slices, filters or breaks out of its loop, and asserts the breakdown renders before the rows rather than after them. A breakdown that drops a row is indistinguishable from a shorter gate, which is the one direction a release page must never be wrong in. Proved on a mutant: capping the loop at ten rows fails it.

Below eight rows there is no breakdown — a tally of four over a list of four says nothing the list does not, and `GATE_BREAKDOWN_MIN` states that as one decision rather than a literal in a condition.

## Independent review — 2026-08-20

Fresh-context pass, separate session, `model:claude-opus-5`. Started from the notes and the diff `222e19e..6cc7f72`; the author's reasoning trace was not available to it. Verdict: **changes-requested**.

**The motivating surface is not the one `your-trainer` renders.** `buildGateSection` draws the single `Blocking` list only in the `else` of `if (delta?.comparable)`. `your-trainer` has release tags, so `delta.comparable` is `true` (baseline `v2.1.6`) and the page renders `New` / `Chronic` / `Regressed` instead — the `Blocking` branch is the *"eleven of twelve repos have no release tag"* path. Measured there: `New` 22 rows / 3 areas, `Chronic` 20 rows / **13** areas (eight of them singletons), `Regressed` 0. The 59-rows-across-17-areas shape, and *"two areas are more than half the gate"*, describes a list that repo's release page does not draw.

That also undercuts `GATE_BREAKDOWN_MIN`: the threshold is on **row count**, but what makes a tally useful is **concentration**. `Chronic`'s 20 rows over 13 areas is the *"tally of four over a list of four"* the constant exists to prevent, at a larger row count and therefore admitted.

**Lossless is claimed, not asserted, and one chip already links to nothing.** `gateAreaBreakdown` buckets an empty area under `'\u2014'`, but `checkMatches` compares `f.areas.has(item.area || '')` — so a `—` chip navigates to `~checks/area/%E2%80%94` and matches **zero** rows. On `your-trainer`'s `New` group that chip currently stands for 5 rows. (There is also a trim asymmetry: the chip key is `.trim()`ed, the filter is not.) `test_the_gate_breakdown_is_lossless_and_sums_to_its_list` only forbids `slice(` / `filter(` / `break;`; the mutant `if (!item.area) continue;` inside the tally loop drops rows and **165 passed**. The property named — *"a breakdown that drops a row is indistinguishable from a shorter gate, the one direction a release page must never be wrong in"* — is not tested.

Also: `59` is neither basis. At `your-trainer` HEAD the gate is 68 across 19 areas (`Monetization & Licensing` 13, not 11); 59 is the working tree *before* `ISS-0213`'s relevelling, which took it to 62. And the JSDoc `/** One group of gate rows … */` now sits above `const GATE_BREAKDOWN_MIN = 8;` rather than above `function gateGroup`, and the CSS comment `/* An automated check's row (ADR-0039) … a manual row carries its mark button */` now heads `.gate-breakdown` — stale as well as detached, since `ISS-0243` is what moved the command out of that slot.

## Independent review — second pass, 2026-08-20

**This supersedes the first-pass verdict above. Current verdict: changes-requested.** Same reviewer, same conditions — fresh context, separate session, `model:claude-opus-5` — re-run against the working tree after the first pass's findings were acted on. Every claim below was re-measured or re-executed rather than read.

Two of three findings are closed and verified. The em-dash chip is genuinely fixed — the key is the raw area, the label is applied at render, and `test_the_breakdown_chip_opens_rows_that_exist` asserts the round trip against `checkMatches`'s own comparison. Restoring the em-dash key fails it. The branch finding is recorded honestly at the call site: the condition was already right, and what was wrong was the reasoning printed beside it.

**The lossless guard is still a word-list, one level up, and a row-dropping mutant passes.** The new version parses the loop and forbids `continue`/`return`/`break` inside it — which does catch my original mutant (executed, fails). But nothing requires the accumulation to be *unconditional*:

```ts
if (area) byArea.set(area, (byArea.get(area) || 0) + 1);
```

iterates `items`, contains no escape keyword, and holds exactly one `byArea.set(` — so it satisfies every assertion, and **165 passed** (executed). It silently drops the no-area rows, which on `your-trainer`'s `New` group is 5 of 22. The property the docstring names — *"the parts must sum to the list"* — is still unasserted, and it is the one direction the note says a release page must never be wrong in. Either assert the accumulation is the whole loop body (no `if` between `for` and `byArea.set`), or accept that a source-text guard cannot express a sum and say so in the docstring instead of claiming it.

**Still open from the first pass, both believed fixed:** the JSDoc `/** One group of gate rows … */` still sits directly above `const GATE_BREAKDOWN_MIN = 8;` (renderer.ts:8884), and `renderer.css:6102` still stacks three comment blocks above `.gate-breakdown`, the first of which describes `.checks-row-command` and is itself stale (*"a manual row carries its mark button"* — this range moved it). That CSS comment also still reads *"`your-trainer` puts 59 rows here across 17 areas"* with no basis caveat — a site the sweep missed, along with `renderer.ts:8628`, `renderer.ts:8899`, `cockpit.py:4592`, `cockpit.py:4743` and `cockpit.py:4804`.
