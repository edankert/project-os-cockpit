---
type: "[[issue]]"
id: ISS-0049
aliases: ["ISS-0049"]
title: "The design-token parity check has no caller, and three notes claimed it did"
status: triage
severity: high
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["independent review of FEAT-0042, 2026-07-28"]
related: ["[[TASK-0219-Design-Token-Parity]]", "[[FEAT-0042-Design-Bench]]", "[[DES-0002-Cockpit-Design-System]]", "[[ISS-0023-Status-Vocabulary-Drift]]"]
fixed_by: []
---

# A guard nobody calls

## Refuted by mutation

`--status-done` changed in `base.css` from `hsl(160 28% 38%)` to `hsl(160 28% 41%)`, no design note touched: **459 passed, 1 skipped.** Reproduced independently after the reviewer reported it.

`design_tokens.check_design_assets()` is called from `tests/test_design_tokens.py` and **nowhere else** — not `validate-docs.py`, not any endpoint, not the pre-commit hook. And it would be silent regardless: it scans artifacts for `--status-*`/`--severity-*` declarations, and no artifact in the repo declares one. The divergence tests compare two hand-written strings inside the test module, so no implementation change can perturb them.

## Three notes asserted otherwise

- [[FEAT-0042]] Acceptance: *"A design token changed in the implementation but not the design note fails a test, and the test fails when the fix is reverted (adequacy, per QUALITY.md)"*
- [[PHASE-009]] exit criterion, **ticked**: *"A design token changed in the implementation is caught by a test"*
- [[DES-0002]] Conformance: *"It is the thing TASK-0219 still guards"*

All three corrected on 2026-07-28. [[TASK-0219]]'s own Result section was honest — it records that the check is silent on the only artifact in the repo. The three claims above it were written as though it were not.

**This is the ISS-0024 pattern at the level of a feature's acceptance**: a guard described more widely than it guards, three times over, in the notes rather than in a docstring. The measurement that would have refuted any of them takes one line and was never run.

## What a real fix requires

Not just wiring the checker into the validator — that would still be silent, because nothing declares tokens to compare. The honest options:

1. **Drop the claim.** The design bench does not check token parity; `statuses.py` + [[TST-0019]] guard the implementation's own vocabulary, which is where drift actually happened ([[ISS-0023]]). Cheapest and arguably correct.
2. **Check the note's prose table** against `base.css`. That is the artifact that *can* drift and the one DES-0002 pointed at. Needs a Markdown-table parser and a name mapping.
3. **Require artifacts that show status colour to declare their tokens**, then wire `check_design_assets` into the validator. Makes the check real but imposes a rule on every future artifact.

Not chosen here. Recording the refutation and correcting the false claims is the finding; picking the fix is Edwin's.
