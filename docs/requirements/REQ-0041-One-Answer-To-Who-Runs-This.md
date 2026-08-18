---
type: "[[requirement]]"
id: REQ-0041
aliases: ["REQ-0041"]
title: "One answer to 'who runs this' — the reader and the registry must never disagree about a test"
status: draft
phase: "[[PHASE-036-One-Human-Walk]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
priority: high
scope: "obligation registry"
implements: "[[FEAT-0122-One-Human-Walked-Population]]"
acceptance:
  - "[ ] One predicate decides who runs a test. `cockpit._is_manual_test` and `obligations._is_owed` agree on every test in every repo — they disagree on 8 of 788 today, and none of the 8 involves a `command:`, so it is latent rather than live."
  - "[ ] `kind:` is gone from the schema and from every note. `command:` answers who runs a test and nothing else claims to — a constraint would leave two fields and add a rule (ADR-0034 decision 4)."
  - "[ ] The Tests badge is derived from the tiers and is not larger than the number it replaced, per repo. Baseline: project-os-cockpit 1, your-sudoku 0, your-trainer 5."
  - "[ ] No acceptance row reaches a badge. ADR-0027 survives ADR-0033 untouched, and the guard that asserts it stays green."
covers: []
related: ["[[ADR-0033-A-Manual-Test-Is-An-Acceptance-Test]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]"]
---

# One answer to who runs this

Two predicates decide this today and they are written in different places: the reader asks `command:` first, and the registry asks whether `kind`/`level`/`runner` contains the word *manual* and never reads `command:` at all. **The registry's is the one that fills `Needs a run` and the badge** — so the surface a person acts on is driven by the weaker rule.

Eight tests disagree between them fleet-wide. None involves a `command:`, which is why nothing has broken yet and also why nothing would announce it when it does.
