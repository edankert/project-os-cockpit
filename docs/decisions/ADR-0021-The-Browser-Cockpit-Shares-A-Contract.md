---
type: "[[decision]]"
id: ADR-0021
aliases: ["ADR-0021"]
title: "The browser cockpit stays, and stops being hand-written — the two front doors share a generated contract instead of two maintained twins"
status: proposed
date: 2026-08-11
owner: user:edwin
supersedes: []
superseded_by: ""
related: ["[[TASK-0321]]", "[[FEAT-0073-One-Voice]]", "[[FEAT-0084]]", "[[ADR-0010]]", "[[PHASE-029-One-Tool-Two-Front-Doors]]", "[[PHASE-026-The-Returning-Human]]"]
tags: [decision]
---

# The browser cockpit shares a contract

## Status

`proposed` — deliberately. This decision arrives for the actuator row on the Intent view, which is where a person accepts or rejects it. An ADR that authored itself into `accepted` would be the tool granting itself a decision the record says is a human's.

## Context

The cockpit has two front doors:

| | lines | vocabulary |
|---|---|---|
| mode 3 — Electron renderer | 13,982 TS + 5,168 CSS | 10 nav modes |
| mode 1 — browser cockpit | 2,124 JS + 1,796 CSS | 4 nav modes |

They are **hand-written twins**. Nothing generates one from the other, nothing compares them, and every shared idea is declared twice.

### The cost, measured rather than asserted

[[FEAT-0073]] opened on *"three drifts in two days, all caught by review, none by tests-as-first-written."* On 2026-08-11 a fourth arrived, and it was not caught by review:

> [[ISS-0131]]'s fix edited `.nav-group:has(> .nav-group-header.is-thing)` in `renderer.css`, rebuilt, reloaded — and **changed nothing on screen**. `cockpit.css` carries its own copy of the same rule, the desktop shell loads **both**, and cockpit.css wins. The change was correct, built and deployed while the surface it targeted was governed by the other file.

It was found by Edwin looking at the screen and saying *"I don't see the cards"*. That is the failure mode this ADR exists to price: **a UI change can be complete, correct and verified against the file its author edited, and still be inert.**

Related, same day: [[ISS-0135]] — the standing documents were dead clicks because one builder emitted `/README.md` where every other emits `/docs/README.md`. That is [[ISS-0037]]'s defect recurring in a new surface, and ISS-0037 was itself a two-doors problem.

### The audience, which is real

Mode 1 is not vestigial. The render server binds `0.0.0.0` **on purpose** so a tablet on the same Wi-Fi can read the record — a stated use in `CLAUDE.md`, and the reason the loopback guard on writes exists separately from the bind. Hover does not exist on that device, which is why [[ISS-0133]] left the badge explanation unfinished. Retiring mode 1 would delete a real reading surface to solve a maintenance problem.

## Options

1. **Retire mode 1.** Cheapest maintenance, deletes the tablet read path. Rejected: it solves the cost by discarding the audience.
2. **Fund it.** Keep both hand-written, accept the doubling, add review discipline. Rejected: review discipline is what already failed — three of four drifts were caught by review and the fourth was not, so the mitigation has a measured miss rate.
3. **Scope it.** Freeze mode 1 as a read-only subset and stop porting. Partially true already (it has 4 modes to mode 3's 10) and it does not help: the twin stylesheet that broke today is in the *shared* part, not the divergent part.
4. **Share the contract.** One declared vocabulary and one set of shared rules, consumed by both renderers.

## Decision

**Option 4.** Mode 1 stays, and stops being a hand-maintained twin.

The evidence for this is comparative rather than aspirational. `t3.codes` serves **three** client surfaces — web, Electron, React Native — from one shared typed schema package, and does not suffer vocabulary drift. The cockpit has **two** surfaces, no shared schema, and drifted four times in a week.

**So the drift is not evidence that two surfaces are unaffordable. It is evidence that two *hand-written* surfaces are.** That distinction is the whole decision: the cost being paid is not the cost of having a browser door, it is the cost of declaring everything twice.

### What this commits to

- The view vocabulary is declared **once** and consumed by both renderers — which is [[FEAT-0084]] exactly, and this ADR is its justification rather than a competing plan.
- Rules that both doors share (the group card, the empty-state voice, the nav-url shape) live in one place, or are asserted across both by a test that reads **both files**. Today's fixes did the second: `test_a_thing_head_is_framed_like_every_other_group` and `test_the_phase_head_sits_left_of_its_features` now read `renderer.css` **and** `cockpit.css`, so a one-sided edit fails the suite instead of looking fixed.
- New shared surfaces are added to the contract, not to both files.

### What it does not commit to

- Rewriting mode 1 to match mode 3 feature-for-feature. Parity is **not** the goal — [[ADR-0010]] decides what the read-only door is *for*, and it is still `proposed`. This ADR says the two doors must not drift; it does not say they must be the same.
- A build step for the browser cockpit. "No build step" is a property of this project (`CLAUDE.md`), and a shared contract can be a generated JSON or a single JS module both load.
- Doing it now. [[PHASE-029]] owns the work and is explicitly **out** of [[REL-0001]] (Edwin, 2026-08-11).

## Consequences

- **Immediate, and already paid**: cross-file tests are the interim mitigation. They are strictly worse than one declaration — they catch divergence rather than prevent it — but they turn a silent inert edit into a failing test, which is the difference between today's bug and today's bug being found by the person using the app.
- Until FEAT-0084 lands, **every shared UI change must edit both files**, and the reviewer's question is "which file governs this on screen?" rather than "is this change correct?"
- If this is rejected, the honest alternative is option 1 — retire mode 1 — because option 2's mitigation has now missed once in four, and paying the doubling while pretending review catches it is the worst of the four.
