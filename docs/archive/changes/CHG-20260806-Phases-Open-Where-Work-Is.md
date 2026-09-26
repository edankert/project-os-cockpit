---
type: "[[change]]"
id: CHG-20260806-Phases-Open-Where-Work-Is
title: "The project overview expands a phase on first paint only where work is happening — active status and something in flight"
status: merged
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
source: ["Edwin 2026-08-06: 'On the project overview page, can we collapse by default any phases which are not active or which do not have any in-flight items?'"]
commit: ""
pr: ""
impacts: [desktop-renderer]
issues: ["[[ISS-0103-Every-Live-Phase-Opens-Its-Strip]]"]
features: []
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[PHASE-016-The-Overview-Answers-Questions]]", "[[FEAT-0056-Completed-Work-Ordering]]", "[[TST-0023-Completed-Work-Ordering]]"]
---

# Phases open where work is

## Summary

The overview's phase accordion defaulted to `!complete` — every unfinished phase expanded its item strip on first paint. It now expands only when the phase's status says someone is in it (`active` or `doing`) **and** something under it is in flight. Both conditions, not either.

Measured on first paint, before → after:

```
                      phases open      squares painted   section height
project-os-cockpit    7 of 7 → 1 of 7  99 → 7            655px → 487px
your-health           6 of 6 → 1 of 6  303 → 142         580px → 440px
```

This is a **default, not a filter**. Every row keeps its id, title, progress, attention count and state, and one click opens it; the stored per-phase state still wins, so an SSE re-render never re-collapses what the reader opened.

## Impact

- Mode 3 only — mode 1's `cockpit.js` has no phase accordion, so there is no twin to keep in step.
- Mode 3 is a built bundle: live after the desktop app restarts.
- No payload, endpoint or note-format change.
- `sortLivePhases` is refactored to ask the same `phaseIsActiveStatus` predicate the new rule uses. Ordering is unchanged — the active phase still leads — but "which statuses are active" now has one definition instead of two.

## Where the decision lives

In `completed-work.ts` as a pure predicate, for the reason that module's header gives: a decision inside a DOM function can only be guarded by grepping the built bundle, and that guard survives the mutation that breaks it. It is tested as a truth table in `fleet-health.test.mjs`; the wiring — that `phaseIsOpen` consults it, feeds it the same `countInFlight(p)` the row prints, and still lets a stored state win — is checked in `test_completed_work_ordering.py`.

Mutation-checked eleven ways across both suites; all eleven caught.

## Documentation Coverage (All Types Considered)

- features: not-applicable
- requirements: not-applicable
- tasks: not-applicable
- issues: new
- tests: updated
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new
- snapshot: updated

## Follow-ups

- [ ] A collapsed phase row is 66px for 23px of content; the other 43px is card padding. Closing five strips only took your-health's phase section from 580px to 440px because of it.
- [ ] `.ov-phase` has two rule blocks 380 lines apart (`display: block` + padding/border, then `display: flex` + gap/margin). The second wins for shared properties. Same first-match trap [[ISS-0100]] removed for `.scoped-feat`; the block-count guard covers only two selectors.
