---
type: "[[decision]]"
id: ADR-0022
aliases: ["ADR-0022"]
title: "Whether a delegate may push — the status quo holds until this is accepted, and the deploy refusal is untouchable in every option"
status: proposed
date: 2026-08-11
owner: user:edwin
supersedes: []
superseded_by: ""
related: ["[[TASK-0328]]", "[[FEAT-0075-The-Delegation-Policy]]", "[[ADR-0009-The-Principal-Is-A-Role]]", "[[FEAT-0055]]", "[[RISK-0006]]", "[[PHASE-027-The-Standing-Worker]]"]
tags: [decision]
---

# Whether a delegate may push

## Status

`proposed` — for the principal, through the actuator row. **Until it is accepted, the worker's relationship to `git push` is: never.** That is not a placeholder; it is the operative rule while this note is unaccepted, and it is why the note can sit here safely.

## Context

[[ADR-0009]] named pushing explicitly **so that it could not relax as a side effect**. This ADR is where it may relax *as a decision* — and that distinction is the whole deliverable. A capability that widens because nobody noticed is the failure mode; a capability that widens because somebody wrote down why is governance.

Three facts frame it:

1. **A commit is local and reversible; a push is publishing.** Once a forge has cached and indexed it, deleting does not unpublish. [[FEAT-0055]] drew this line for close-out and it has held: *"it does not push, and nothing else does either."*
2. **One fleet repo's only remote is a server path.** Pushing it deploys a live website. This is not a hypothetical about some future repo — it is a repo in `~/Dev/repos/` today, and it is why the fleet roll-up's push action refuses deploy remotes rather than warning about them.
3. **[[RISK-0006]]'s second hazard is spend, and its third is audit lag.** A delegate that publishes adds a fourth: reach. A wrong judgment that stayed local is recoverable by `git reset`; one that was pushed is recoverable only by asking other people to do something.

## Options

### 1. The human publishes, on cadence (status quo)

The worker commits; a person pushes when they look. Costs a round-trip per publish and bounds the blast radius of every autonomous mistake to one machine.

### 2. Scoped delegation — non-deploy remotes only

The delegate may push where a push cannot deploy. Requires the cockpit to classify remotes, which it already does for the roll-up's refusal, so the mechanism exists.

The weakness is that the classification is a **guess about somebody else's infrastructure**. A remote that is not a deploy target today becomes one when a hook is added, and nothing tells the cockpit.

### 3. Full delegation, deploy-refusal untouchable

The delegate pushes wherever a human could, except deploy remotes, which stay refused for everyone. Cheapest to operate, and it makes the deploy refusal load-bearing in a way it has never been tested as.

## Decision

**Option 1 — the status quo — is what this ADR proposes to keep**, and the reasoning is that the case for changing it has not been made by anything measured.

The argument for 2 or 3 is convenience: a human round-trip per publish. Against that: [[RISK-0006]] is `open`, the supervised week it requires has not been run, and **no delegate has yet made a single autonomous judgment in this repo**. Widening publication rights before the loop has demonstrated it can be trusted with *local* work is arguing from an inconvenience nobody has actually experienced.

Option 2 is the one to revisit first, and the condition for revisiting it is stated so it is not a feeling: **after RISK-0006's supervised week, with the ledger showing what the delegate actually did.** If the week produces no corrections, the round-trip cost is real and the risk is measured rather than imagined.

## Consequences

- The worker never pushes. `FEAT-0055`'s line stands unchanged, and the delegation policy's *"what is never delegated"* section names pushing among the four.
- **The deploy refusal is untouchable in every option**, including the ones this rejects. No delegation may reach it, and no policy line may name it — which is worth stating even under option 1, so a later widening cannot quietly acquire it.
- Revisiting is scheduled against evidence rather than a date: the supervised week's ledger.
