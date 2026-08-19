---
type: "[[task]]"
id: TASK-0533
aliases: ["TASK-0533"]
title: "The run list is a query — no terminal entry since the last invalidation, and not covered by this cycle's CI"
status: backlog
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
parent: "[[FEAT-0135-Everything-Downstream-Is-A-Query]]"
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
tags: [task]
---

# What a person has to run

## Definition of Done

- [ ] `run_list(platform, subjects=None)` returns checks with no terminal entry since their most recent invalidation.
- [ ] A check with **no entry at all** for that platform is in the list — the absence is the initial state ([[REQ-0054]]).
- [ ] An `na` entry removes a check from the list until something invalidates it.
- [ ] An `excused` entry removes it **for that release only** — after the seal the check is owed again, with no action by anybody ([[ADR-0037]] decision 7).
- [ ] Entries whose `method: automated` came from this cycle's CI are excluded.
- [ ] One implementation; the badge, the tests view and the release page all call it.

## Notes

*Run*, not *walk* — [[DES-0012]] D5 and [[TASK-0521]]. One verb: a test with a command is run by a runner, one without is run by a person. That property survived being argued in both directions and should not be re-litigated here.

The invalidation cursor is what `mark: rerun` was reaching for. As an event with a date it needs no value ([[ADR-0037]] decision 5).
