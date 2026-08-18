---
type: "[[task]]"
id: TASK-0495
aliases: ["TASK-0495"]
title: "One verb for one act — the registry carries `Run` and `Walk` over the same type today"
status: backlog
phase: "[[PHASE-036-One-Human-Walk]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
source: ["[[FEAT-0123-The-Walk-Surfaces-Say-One-Thing]]"]
parent: "[[FEAT-0123-The-Walk-Surfaces-Say-One-Thing]]"
effort: S
depends: ["[[TASK-0492-Retire-The-Manual-Run-Obligation]]"]
blocks: []
related: []
tests: []
---

# One verb

The registry carries both simultaneously: `test → Run` and `release gate → Walk`, over one type. Live on `your-trainer` as **`Run 5 tests`** and **`Walk 1 release gate`** on the same screen.

The split made sense while they were different types. Under [[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]] they are one type on a scale, so the surface has two words for one act separated by a field the reader cannot see — and it shows: the group called **`Needs a run`** contains only the NON-acceptance tests, while the population a person actually walks sits under `Tier 1/2/3` with no verb at all.

Pick one deliberately. *Walk* describes what a person does to a checklist; *Run* describes what a machine does to a command — which is an argument for `Walk` on the human side and `Run` staying with `command:`. Apply it to the registry verbs, the group headings and the buttons in one pass, or the two words simply move.

Done when: one verb names the human act everywhere, and `run` refers only to something a machine does.

## Not done, and deliberately last

The vocabulary change is the one piece of FEAT-0123 that touches every surface at once — registry verbs, group headings, buttons — and it is the one with no measurement behind it: *walk* versus *run* is a naming judgement, where the other three tasks each had a number.

It is also now smaller than when it was written. `Needs a run` still contains only non-acceptance tests, but under [[ADR-0034-Three-Axes-Not-One-Word]] that is no longer a *different kind of test* — it is the same population filtered by execution. Renaming it is a one-line change once somebody picks the word.

**Recommendation on the record**: *walk* for the human act and *run* for what a machine does to a `command:`, which is the split the two words already carry in ordinary use and the one `command:` makes structural.
