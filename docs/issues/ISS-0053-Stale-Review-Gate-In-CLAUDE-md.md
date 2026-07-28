---
type: "[[issue]]"
id: ISS-0053
aliases: ["ISS-0053"]
title: "CLAUDE.md stated a review gate that ADR-0013 had already retired"
status: fixed
severity: medium
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["Edwin, 2026-07-28: 'I thought we agreed/proven to use the same model but with a clear context instead?'"]
related: ["[[ISS-0023-Status-Vocabulary-Drift]]", "[[ISS-0049-Token-Parity-Check-Has-No-Caller]]"]
fixed_by: []
---

# One rule, two places, and the stale one is the one everybody reads

`CLAUDE.md` said:

> QUALITY.md requires a different model *family* or a human … A same-family review does not close that gate — record a cross-vendor or human pass manually when it matters.

`tools/instructions/QUALITY.md` line 49 says:

> Model family is **not** the gate (ADR-0013) … The mechanism that makes a reviewer independent is not having been present while the work was rationalised.

ADR-0013 retired the family rule after an experiment refuted its premise. `CLAUDE.md` was never updated.

## What it cost

`CLAUDE.md` is loaded into **every session's context**, ahead of anything in `tools/instructions/`. So:

- Two independent reviewers, in separate clean-context sessions, both reported that a cross-vendor pass was "still owed" on FEAT-0043 and FEAT-0042.
- The agent relayed that to Edwin **three times** without checking the contract it was quoting.
- Edwin caught it: *"I thought we agreed/proven to use the same model but with a clear context instead?"*

Nobody was reasoning badly. Everybody read the copy that was in front of them, and it was wrong.

## The pattern

This is [[ISS-0023]] — one vocabulary restated in N places, drifting — at the level of the operating contract, with an aggravating factor: the stale copy sits in the file with the highest read priority in the repo. A rule that contradicts its own source is worse than a missing rule, because it is *obeyed*.

It also explains something about [[ISS-0049]]: two reviewers found a false acceptance claim by mutation, and neither questioned the review-gate claim they were themselves repeating. Adversarial review checks the work under review; it does not check its own instructions.

## Fix

`CLAUDE.md` now states the ADR-0013 rule and says plainly that there is no cross-vendor requirement. Checked across the fleet: **only this repo carried the stale paragraph**, and every `tools/instructions/QUALITY.md` already had ADR-0013 — so this was a local edit that was never reconciled, not a template drift.

**The review gate on [[FEAT-0042]] and [[FEAT-0043]] is therefore satisfied by the clean-context passes already performed.** No further review is owed for model-family reasons.
