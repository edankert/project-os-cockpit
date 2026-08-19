---
type: "[[task]]"
id: TASK-0535
aliases: ["TASK-0535"]
title: "The cross-platform burndown — A-pass with no terminal B entry, computed, never maintained"
status: done
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
parent: "[[FEAT-0135-Everything-Downstream-Is-A-Query]]"
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
tags: [task]
---

# Where B stands against A

## Definition of Done

- [ ] `burndown(a, b)` returns checks with a terminal `pass` on A and no terminal entry on B.
- [ ] `na` on B drops out by construction, with its reason available. `excused` does **not** drop out — it expired with its release, so the check is owed again.
- [ ] An invalidation on A re-arms **both** platforms, because it invalidates *the check*.
- [ ] Proved on a fixture with one Android pass, one iOS gap, one iOS `na` and one invalidation.

## Notes

**The re-arming is the structural fix for the `ISS-0365`/`ISS-0366` class in `your-trainer`** — an iOS twin of an Android fix that never crossed, invisible because the matrix row already said DONE. Under per-behaviour checks the fix invalidates the check and both platform verdicts re-arm at once.

**This does not retire `PARITY_MATRIX`.** The matrix's first failure mode is a surface with no row, which no query over checks can see; that is [[FEAT-0130]]'s `SUR-*` work. What this subsumes is the matrix's verdict columns and its in-matrix back-port table. The retirement decision belongs to `your-trainer`, after [[FEAT-0130]].

## Done 2026-08-19

`ledger.burndown(docs_root, a, b)` — A-`pass` with no surviving verdict on B. **`na` drops out by construction** (a ruled-inapplicable check has a verdict on B, so it is not a gap) and **`excused` does not**, because it expired with its release and the check is owed again. That asymmetry is the whole reason they are two values.

`test_an_android_fix_re_arms_both_platforms_at_once` pins the payoff [[ADR-0037]] names: an invalidation names **the check**, not a platform's copy of it, so a fix landing on Android puts the check back in the owed set on iOS too — the structural fix for the `ISS-0365`/`ISS-0366` class.

**No rendered view.** The query exists; nothing draws it, and `PARITY_MATRIX` is untouched — which is correct, because retiring it needs [[FEAT-0130]] first.
