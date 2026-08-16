---
type: "[[task]]"
id: TASK-0439
aliases: ["TASK-0439"]
title: "The next release accumulates — Publication always shows what has landed since the last ship, derived, with no note until somebody declares one"
status: done
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["Edwin 2026-08-16: 'there is always a release and any features/phases/issues etc … committed/pushed after the previous release are naturally part of the new release'"]
parent: "[[FEAT-0105-There-Is-Always-A-Release]]"
effort: M
depends: ["[[TASK-0438-Preparing-Is-A-Flag-Not-A-Status]]"]
blocks: []
related: ["[[FEAT-0072]]", "[[ADR-0022]]"]
tests: ["[[TST-0032-The-Release-Accumulates-Then-Asks]]"]
---

# The next release accumulates

## What

A rung that is always present: *"Next release · accumulating — 12 features, 8 issues since REL-0012"*, with `Prepare ▸`.

**Derived, with no note.** `unreleased_payload` ([[FEAT-0072]]) already computes *done but not shipped*: a feature is shipped when a `released` note names it in `features:`. The open release needs no list of its own and no note until somebody declares a version.

**No dates.** Edwin described membership as *"committed/pushed after the previous release"*. [[FEAT-0072]] deliberately rejected dates — features carry no completion timestamp and `updated:` moves for a typo — and it does not matter: *unshipped* already means *no released note names it*, which is the same set without a clock.

## Definition of done

- [ ] The rung is present in every repo that has ever shipped a release, and in one that never has it says so rather than rendering blank
- [ ] Membership comes from `unreleased_payload` — no second computation, no dates
- [ ] It asks nothing while accumulating: no badge, no obligation
- [ ] `Prepare ▸` writes the note and sets `preparing:`; nothing is auto-written before that
- [ ] Once preparing, the rung names the release and the gate asks
- [ ] On ship, `features:` is frozen into the note from the derived set and exceptions reset to `[ ]`
- [ ] Nothing here publishes ([[ADR-0022]])
