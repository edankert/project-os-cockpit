---
type: "[[task]]"
id: TASK-0321
aliases: ["TASK-0321"]
title: "Mode 1 decided once, with the drift record as evidence"
status: done
phase: "[[PHASE-026-The-Returning-Human]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[FEAT-0073-One-Voice]]"]
parent: "[[FEAT-0073-One-Voice]]"
effort: M
depends: []
blocks: []
related: []
tests: []
---

# Mode 1 decided once, with the drift record as evidence

## Definition of Done

- An ADR weighs mode 1's audience (the tablet read case) against its cost (three twin-drifts in two days, every UI change doubled); it retires, funds, scopes, or **shares the contract** — and the decision arrives `proposed` for the actuator row.
- **The fourth option is new, and it is evidence rather than opinion** (t3.codes comparison, 2026-08-05): T3 serves **three** client surfaces — web, Electron desktop, React Native mobile — from one shared typed schema package, and does not suffer vocabulary drift. The cockpit has **two** surfaces, no shared schema, and drifted three times in two days. The ADR must address this directly: the drift is not evidence that two surfaces are unaffordable, it is evidence that two *hand-written* surfaces are.

## Done — 2026-08-11

[[ADR-0021]], `proposed` — it arrives for the actuator row rather than accepting itself, because an ADR that authored itself into `accepted` would be the tool granting itself a decision the record says is a human's.

**It chooses the fourth option: share the contract.** Mode 1 stays — the `0.0.0.0` bind exists so a tablet can read, which is a real audience, and retiring it would solve a maintenance problem by deleting a reading surface. What goes is the *hand-writing*.

**The task asked for the drift record as evidence, and the record grew while this was being written.** FEAT-0073 opened on *"three drifts in two days, all caught by review"*. A fourth arrived on 2026-08-11 and was **not** caught by review: [[ISS-0131]]'s card fix edited `renderer.css`, built, reloaded, and changed nothing, because `cockpit.css` carries the same rule and wins. Edwin found it by looking at the screen. That moves option 2 (fund it, rely on review) from "expensive" to "measurably unreliable" — three of four caught, one missed, on the surface the reader sees.

The t3.codes comparison is carried into the decision as the task required: three client surfaces from one shared schema, no drift, against this project's two surfaces, no schema, four drifts. **The drift is not evidence that two surfaces are unaffordable; it is evidence that two hand-written surfaces are.**

Measured for the ADR: mode 3 is 13,982 TS + 5,168 CSS with 10 nav modes; mode 1 is 2,124 JS + 1,796 CSS with 4.

The interim mitigation is already in place from today's fixes — the two CSS guards now read **both** stylesheets, so a one-sided edit fails the suite instead of looking fixed. That is strictly worse than one declaration (it catches divergence rather than preventing it) and is stated as such in the ADR's consequences.
