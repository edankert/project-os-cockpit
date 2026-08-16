---
type: "[[task]]"
id: TASK-0438
aliases: ["TASK-0438"]
title: "`preparing` is a flag, not a status — the gate asks when a person declares intent to ship, never merely because a release is open"
status: done
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["[[FEAT-0105]] — being open and being prepared for ship are different facts, and only the second is a debt"]
parent: "[[FEAT-0105-There-Is-Always-A-Release]]"
effort: M
depends: []
blocks: ["[[TASK-0439-The-Next-Release-Accumulates]]"]
related: ["[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[DES-0006]]"]
tests: ["[[TST-0032-The-Release-Accumulates-Then-Asks]]"]
---

# `preparing` is a flag, not a status

## What

`preparing: <date>` in a `draft` release's frontmatter. The acceptance gate asks on **that**, not on `draft`.

`STATUSES.md` allows a release `draft`, `released`, `reverted` and is template-owned, so adding vocabulary there would report as divergence on the next sync. [[DES-0006]] already established this exact pattern and `obligations.py` already documents it for features: *"`acceptance: requested` in frontmatter, not a status."*

## Why the state has to exist

If a release is always open and the gate asks whenever one exists, **the gate asks forever** — the self-re-arming badge [[ADR-0027]] excludes staleness for, and the failure [[PHASE-034]] was opened to avoid producing.

## Definition of done

- [ ] `publication.preparing()` requires the flag, not just `draft`
- [ ] A `draft` release without it is **open**: shown, accumulating, asking nothing
- [ ] The gate contributes zero obligations while a release is open and one while it is preparing
- [ ] `Prepare ▸` sets the flag and the version in one act
- [ ] The overtaken-draft rule still holds: a draft below the newest `released` is neither open nor preparing, it is stale ([[FEAT-0102]])
- [ ] `[!]` is refused unless a release is preparing ([[TASK-0435]])
