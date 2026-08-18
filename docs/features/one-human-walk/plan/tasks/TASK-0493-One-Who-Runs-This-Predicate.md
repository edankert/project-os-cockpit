---
type: "[[task]]"
id: TASK-0493
aliases: ["TASK-0493"]
title: "One predicate for "who runs this", and the eight notes that currently disagree"
status: backlog
phase: "[[PHASE-036-One-Human-Walk]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
source: ["[[FEAT-0122-One-Human-Walked-Population]]"]
parent: "[[FEAT-0122-One-Human-Walked-Population]]"
effort: S
depends: []
blocks: []
related: []
tests: []
---

# One predicate

`cockpit._is_manual_test` reads `command:` first, then `kind`/`automation`/`mode`/`method`, then the body. `obligations._is_owed` asks whether `kind`/`level`/`runner` contains *manual* and **never reads `command:`**.

**The registry's is the one that fills `Needs a run` and the badge**, so the surface a person acts on runs on the weaker rule. Measured fleet-wide: **8 of 788 tests disagree**. None involves a `command:`, which is why nothing has broken — and why nothing would announce it when it does.

The reader's rule survives; the registry calls it. Guard on the two agreeing across every test in every repo rather than on the eight, because the eight are today's symptom and the disagreement is the defect.

Done when: one predicate, called from both places, and a guard that fails if they ever diverge again.
