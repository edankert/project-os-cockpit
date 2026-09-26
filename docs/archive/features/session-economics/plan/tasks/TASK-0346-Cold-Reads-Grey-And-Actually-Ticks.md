---
type: "[[task]]"
id: TASK-0346
aliases: ["TASK-0346"]
title: "A cold session reads grey on the rail, and the transition happens on a clock rather than on an event that will never come"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
source: ["user:edwin"]
parent: "[[FEAT-0081-What-A-Session-Costs-To-Keep-Alive]]"
effort: M
due: ""
depends: []
blocks: ["[[TASK-0347-Cold-Sessions-Leave-The-Needs-You-List]]"]
related: ["[[ISS-0105-The-Rail-Pulses-The-Same-For-Two-Minutes-And-Two-Hundred-Hours]]"]
tests: []
---

# A cold session reads grey on the rail, and the transition actually happens

## Definition of Done
- [x] Temperature is a **pure function** in its own file (the `health-marks.ts` pattern), taking a timestamp, a clock and a TTL — so it is testable without a DOM or a running app.
- [x] `applyAgentStateToSquare` demotes a cold session to the grey `idle` dot through the same branch `decayed_from` already uses; no new state class, no new colour, no new animation.
- [x] **The dot goes grey with nothing else happening.** A repaint runs on a clock, not only on an inbound agent-state event. This is the requirement — the whole premise is a session where nothing is occurring.
- [x] The tick is cheap enough to run indefinitely and repaints only on disagreement. *(Reworded during implementation: this originally read "when a square's temperature has actually changed", which is the formulation that produced the bug in the Notes below. The condition is now painted-state disagreement, not a remembered temperature.)*
- [x] The square's tooltip says the session is cold and when its last turn was, so grey is explained rather than merely observed.
- [x] A node-suite test proves the transition **across the boundary** — the same input at T+59min and T+61min yields amber then grey — rather than asserting a literal appears in the source.
- [x] `busy` is never demoted: an agent mid-turn is not cold whatever its last state timestamp says.

## Steps
- [x] `desktop/src/renderer/cache-temperature.ts` — global, no imports/exports, matching `health-marks.ts`.
- [x] Use it in `applyAgentStateToSquare`; extend the tooltip.
- [x] A repaint tick beside the existing 30s `updateLiveDurations` interval.
- [x] `desktop/tests/cache-temperature.test.mjs` against the built file.

## Notes

**The optimisation that broke the feature, found in verification.** The first implementation cached the last computed temperature per workspace and repainted only on a change. It passed the unit tests and the first end-to-end check, then failed the second: the DOM is *also* repainted by inbound SSE events, so after cold → warm (event) → cold (time) the cache still read `cold`, the tick saw no change, and the dot stayed amber permanently. The failure mode was precisely the one this task exists to prevent, and it was invisible to a single-pass test — it needed the cycle run twice.

The fix is to compare against **what is painted** rather than what was last decided: read the square's classes and the panel's rendered row ids, and repaint on disagreement. That is self-healing by construction — the tick cannot hold a stale opinion about the screen, because it asks the screen.

**Verification gap, recorded rather than papered over.** `cacheTemperature` is unit-tested at the boundary in the node suite. The tick's self-healing property is **not** in any suite — proving it needs a DOM, and adding jsdom would contradict the standing decision in `tests/test_desktop_node_suite.py` not to bring a JS test framework into a Python project. It was verified instead by driving three cold → warm → cold cycles against the running app over CDP, all three greying correctly. If this regresses, no test will say so.

**Why `state.ts` is the right clock.** The renderer has no per-workspace transcript, but it has each workspace's last agent-state timestamp, and `waiting` is emitted at turn end — which is when the cache was last written. So `state.ts` is not a proxy for cache age, it is very nearly the same instant, and it is already present for every square without new fleet plumbing.

The 30s tick against a 60min TTL means the grey can lag by up to half a minute. That is the right trade: a tighter tick buys nothing a human would notice, and the existing decay loop in the sidecar already runs at 60s for the same kind of reason.
