---
type: "[[requirement]]"
id: REQ-0041
aliases: ["REQ-0041"]
title: "One answer to 'who runs this' — the reader and the registry must never disagree about a test"
status: implemented
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

## Acceptance criteria

- [x] **One predicate decides who runs a test.** `obligations._is_owed` calls `cockpit._is_manual_test`. Verified across the fleet: 788 tests, **0 disagreements** — it was 8.
- [x] **`kind:` is gone** from `test.md` and from every note fleet-wide: 57 here, 69 in `your-sudoku`, 597 in `your-trainer`, 8 in `your-health`. Deleted rather than constrained, and `test_nothing_declares_who_runs_a_test_except_the_command` fails if a second declaration returns.
- [x] **The badge is not larger than the number it replaced**, per repo: 1 → 1, 0 → 0, 5 → 5, 2 → 2. It *did* move — `your-trainer` went to 8 the moment the predicates were unified, because three frozen per-release suites at `status: ready` started asking to be walked. They are `retired` now, which is what they are.
- [x] **No acceptance row reaches a badge** in any repo.

## Advanced 2026-08-18

The third criterion is the one worth reading. Unifying the predicates **raised a badge before it settled it**, and the rise was correct — the reader was right that those three notes are human-walked, and the registry had been hiding them behind a weaker rule. The fix was to say what the notes actually are, not to re-weaken the predicate.
