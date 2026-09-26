---
type: "[[task]]"
id: TASK-0328
aliases: ["TASK-0328"]
title: "The push decision — publishing under autonomy taken as an ADR, not eroded by convenience"
status: done
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[FEAT-0075-The-Delegation-Policy]]"]
parent: "[[FEAT-0075-The-Delegation-Policy]]"
effort: S
depends: []
blocks: []
related: []
tests: []
---

# The push decision

## Definition of Done

- An ADR weighs: the human publishes on cadence (status quo, FEAT-0055's line) / a scoped delegation for non-deploy remotes only / full delegation with the deploy-refusal untouchable. It arrives `proposed` for the principal.
- ADR-0009 named pushing so it could not relax as a side effect; this ADR is where it may relax **as a decision** — the distinction is the deliverable.
- Until accepted, the worker's relationship to `git push` is: never.

## Done — 2026-08-11

[[ADR-0022]], `proposed` for the principal.

**It proposes keeping the status quo**, and the reasoning is that the case for changing it has not been made by anything measured: [[RISK-0006]] is open, its supervised week has not run, and **no delegate has made a single autonomous judgment in this repo yet**. Arguing for wider publication rights before the loop has shown it can be trusted with *local* work is arguing from an inconvenience nobody has experienced.

All three options are weighed rather than named — status quo, scoped to non-deploy remotes, full with the deploy refusal untouchable — and the middle one's weakness is written down: classifying a remote is a **guess about somebody else's infrastructure**, and a remote that is not a deploy target today becomes one when a hook is added, with nothing telling the cockpit.

**Until it is accepted, the worker's relationship to `git push` is: never.** That is the operative rule while the note is unaccepted, which is what makes it safe for the note to sit there.

Revisiting is scheduled **against evidence rather than a date**: after the supervised week, with the ledger showing what the delegate actually did.

The distinction TASK-0328 asked for is the deliverable and it is stated in the ADR's own context: [[ADR-0009]] named pushing so it could not relax **as a side effect**; this is where it may relax **as a decision**.
