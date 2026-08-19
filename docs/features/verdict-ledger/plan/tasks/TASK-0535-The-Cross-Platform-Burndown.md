---
type: "[[task]]"
id: TASK-0535
aliases: ["TASK-0535"]
title: "The cross-platform burndown — A-pass with no terminal B entry, computed, never maintained"
status: backlog
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
- [ ] `na` on B drops out by construction, with its reason available.
- [ ] An invalidation on A re-arms **both** platforms, because it invalidates *the check*.
- [ ] Proved on a fixture with one Android pass, one iOS gap, one iOS `na` and one invalidation.

## Notes

**The re-arming is the structural fix for the `ISS-0365`/`ISS-0366` class in `your-trainer`** — an iOS twin of an Android fix that never crossed, invisible because the matrix row already said DONE. Under per-behaviour checks the fix invalidates the check and both platform verdicts re-arm at once.

**This does not retire `PARITY_MATRIX`.** The matrix's first failure mode is a surface with no row, which no query over checks can see; that is [[FEAT-0130]]'s `SUR-*` work. What this subsumes is the matrix's verdict columns and its in-matrix back-port table. The retirement decision belongs to `your-trainer`, after [[FEAT-0130]].
