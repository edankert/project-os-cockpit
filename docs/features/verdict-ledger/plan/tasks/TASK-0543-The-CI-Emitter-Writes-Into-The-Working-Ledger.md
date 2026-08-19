---
type: "[[task]]"
id: TASK-0543
aliases: ["TASK-0543"]
title: "The CI emitter appends observed-coverage entries into the working ledger for its platform"
status: backlog
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
parent: "[[FEAT-0138-Coverage-Is-Observed-Not-Declared]]"
phase: "[[PHASE-999-Future]]"
tags: [task]
---

# The emitter

## Definition of Done

- [ ] A green CI run appends one `method: automated` entry per covered check, with `by:` naming the test and `date:` the run.
- [ ] A failing test emits `mark: fail` with the failure as the reason, or emits nothing — decided explicitly, not defaulted.
- [ ] The platform comes from the run's target, and the entry lands in that platform's working ledger.
- [ ] **Deleting a covering test puts its check back on the run list within one CI cycle — proved.**

## Notes

Criterion 4 is the whole point of Stage 2 and the one thing a standing field could not do.

**The limit, and it must not be papered over:** [[ISS-0209]] — the acceptance gate runs in **no repo that holds a check**. Until that is resolved this emitter runs here and nowhere the data lives, so criterion 4 is proved in `project-os-cockpit` only. State that; do not report the fleet as covered.

The failing-test decision matters more than it looks. Emitting `fail` puts a machine-driven population into the release gate — the behaviour change [[ADR-0031]] recorded as a risk rather than discovering later. Same call, same place to record it.
