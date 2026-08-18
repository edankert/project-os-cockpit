---
type: "[[issue]]"
id: ISS-0208
aliases: ["ISS-0208"]
title: "`tier:` still decides whether an attributed check gates — ADR-0034 decision 6 says retire the rule, and nine sites still read it"
status: open
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
severity: medium
component: acceptance
phase: "[[PHASE-999-Future]]"
related: ["[[ADR-0034-Three-Axes-Not-One-Word]]", "[[REQ-0043-Gating-Is-A-Property-Of-The-Link]]", "[[TASK-0499-Backfill-The-Eighty-Three]]"]
---

# The tier rule outlived the reason for it

[[ADR-0034-Three-Axes-Not-One-Word]] decision 6: *"Once gating comes from `covers:`, Tier 1/2/3 stops being load-bearing and survives only if it earns its place as a lifetime field."* Gating now comes from `covers:`. The tier rule did not go.

I tried to close this twice and neither attempt was a fix:

1. **Renamed `GATING_TIERS` to `PERMANENT_TIERS`** and called the criterion met. The second independent verification called it *"the criterion reworded to pass"*. `GATING_TIERS` is still the live name at nine sites, one of them a payload key literally called `gating`.
2. **Claimed the 83 unattributed checks were "all settled"**, which would have made the tier filter harmless. Measured: six are not — `your-trainer`'s TST-0592..0597 are Tier 3, `mark: todo`, cover nothing, never walked.

## The ordering question — tried, measured, reverted, and now yours

The tier filter runs **before** the fail-closed clause, so those six are discarded before the clause that exists for exactly that case can see them. I reversed the order on 2026-08-18 and then reverted it, because measuring it changed what the change meant:

**`your-trainer`'s release gate moves 60 → 66.** And [[TESTING]] says the opposite in as many words — *"Tier 3 tests do not gate releases (they are verification aids, not requirements)."*

The fail-closed clause is justified by *"this check gated yesterday and a purely derived gate would silently stop it gating"*. **That argument does not extend to these six: they never gated under the tier rule either.** So blocking them is not failing closed — it is a **new and tighter gate**, contradicting a written rule, across three repos. That is a decision for you, not a tidy-up at the end of a session, so the code carries the blind spot with a comment pointing here rather than a fix nobody asked for.

**The two honest readings:**

1. **Tier 3 means "one build, then gone" — so an unwalked Tier 3 check is a *stale note*, not a live obligation.** The fix is then to retire or promote those six, and the gate never moves. This is what TESTING.md already implies.
2. **A check that has never been walked has not served its purpose, whatever tier it carries** — a lifetime field should not be able to excuse a verification that never happened. The gate moves to 66 and those six get walked.

Reading 1 is cheaper and consistent with the written rule. Reading 2 is what somebody would expect from a gate that is supposed to fail closed. They differ by six checks in one repo.

## Why it is not closed here

Retirement is conditional on the backfill ([[TASK-0499-Backfill-The-Eighty-Three]]'s successor). Retiring it first would take the release gate from 66 to whatever the unwalked Tier 3 population is across three repos, without anybody having decided that those checks still apply — and *"quieter is the one direction a gate must never move without somebody deciding it"* cuts both ways.

## Done when

- [ ] Edwin picks a reading for the six unwalked Tier 3 checks (retire/promote them, or let them gate).
- [ ] The 83 unattributed checks carry a `covers:` or are retired, so the fail-closed clause is empty.
- [ ] `blocking_for` reads no `tier:`.
- [ ] `GATING_TIERS` is gone, including the `gating` payload key, or is demonstrably presentational only.
- [ ] The gate delta from retirement is measured per repo and stated before it lands.
