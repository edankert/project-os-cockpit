---
type: "[[task]]"
id: TASK-0504
aliases: ["TASK-0504"]
title: "Show the open `TST-*` rows for the features in the release"
status: done
owner: user:edwin
created: 2026-08-18
updated: "2026-08-20"
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: approved
parent: "[[FEAT-0125-The-Release-Page-Reports-What-Holds-It]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# Show the open `TST-*` rows for the features in the release

Edwin: *"these should either show a list of open tsts or suggest something else."* Uses the release's contents — named (FEAT-0129) or derived — to select tests, and shows the ones not settled.

Depends on nothing in FEAT-0129: derived contents work today.

## Done 2026-08-20

`_open_tests_for_contents` in `publication.py`, rendered as **Still to check for these contents** directly under the contents list — a plain list of `TST-*` links with area and covered feature, in the features row's own shape. No marks, no controls ([[ADR-0035]], [[ISS-0244]]).

### The predicate is settledness, and that is the whole difficulty

An acceptance check sits at **`status: active` for its entire life** — the verdict lives in `mark:` and the ledger ([[ADR-0037]]). So the obvious filter, *tests covering a release feature that are not `passing`*, returns every check that covers one:

| filter | rows |
|---|---|
| by `status:` | **94** |
| by **settledness** | **3** |

Measured on `your-trainer`'s working tree, 2026-08-20 (at `HEAD` the contents and suite differ; the shape does not). The first number is an inventory and would have shipped a 94-row wall next to a gate reading 59. Only the second is work.

### Three, beside a gate of fifty-nine

That gap is the feature. The gate counts **every** unsettled check in the repo; this counts the ones covering a feature the release actually carries. On `your-trainer` that is **3 of 66 unsettled** — and the other 63 are checks for features that shipped in or before `REL-0012`, or were never built.

So the section states what it is *not*, in prose, on the page. A reader who sees `3` under a gate that says `59` will otherwise assume one of them is broken, and the guard asserts that sentence is present.

**This is [[ADR-0040]]'s argument arriving from the other end.** That decision reasoned from the gate down — 36 of 39 feature-covering blockers are outside the contents — and this reasons from the contents up to the same 3. Two independent routes to one number is the strongest evidence either of them is right.

### Guarded

`test_the_release_shows_the_tests_owed_for_its_own_contents`, proved on two mutants: dropping the settledness filter (the 94-row wall) and putting a mark class back on the rows. It also anchors on the block's own first line rather than a containing function — the first version anchored on `renderReleasePage` and matched a *different* function ending well above the code, which would have failed for a reason unrelated to the feature.

## Independent review — fourth pass, 2026-08-20

Fresh context, separate session, `model:claude-opus-5`. Verdict: **approved**. Re-measured or re-executed, not read.

Both numbers reproduce on `your-trainer`'s working tree: the release's derived contents hold **32** features, **94** acceptance checks cover them, and **3** are unsettled. The disclaimer is genuinely rendered — `renderer.ts:7950` emits *"…those for features this release does not carry."* — so the `3`-under-a-gate-of-`59` confusion the note predicts is actually addressed on the page rather than only in the note.

The two-independent-routes argument holds: `ADR-0040` reasoned gate-down (36 of 39 feature-covering blockers outside the contents) and this reasons contents-up to the same 3. I re-derived both and they agree.
