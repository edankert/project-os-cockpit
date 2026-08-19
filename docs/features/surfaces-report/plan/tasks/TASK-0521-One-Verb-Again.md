---
type: "[[task]]"
id: TASK-0521
aliases: ["TASK-0521"]
title: "Retire `walk` from the product and the prose; one verb covers both populations"
status: done
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
parent: "[[FEAT-0126-A-Rendered-Mark-Is-A-Check-Mark]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# Retire "walk" from the product and the prose; one verb covers both populations

DES-0012 D5. TASK-0495 changed `Run` → `Walk` because a person walks a procedure and a machine runs a command. D2 (`command:` only) removes that premise, so one verb serves both.

**Invert the guard**, do not delete it: `test_one_verb_names_the_human_act_across_every_owed_kind` currently asserts `Walk` and forbids `Run`.

## Done 2026-08-19

`Run` throughout: the `test` obligation, the release gate, the predicate, the `Needs a run` group label, and the feature-acceptance tooltip. Verified on the payload — every verb the badges render is now `Decide / Accept / Approve / Triage / Run / Push / Deploy / Confirm`, with no `Walk`.

**The guard was inverted, not rewritten.** `test_one_verb_names_the_human_act_across_every_owed_kind` asserted `Walk` and forbade `Run`; it now asserts `Run` and forbids `Walk`. The property under test never changed — **one verb** — and a guard that has to be rebuilt whenever the value moves is asserting the value rather than the property. Mutation-proven: putting `Walk` back fails the suite.

Two other tests carried the old word as an expectation rather than as a subject, and both were updated with the reason attached rather than silently: the release-gate campaign's `verb` assertion, and a landing-page docstring.
