---
type: "[[change]]"
id: CHG-20260806-Cold-Sessions-Read-Grey
aliases: ["CHG-20260806-Cold-Sessions-Read-Grey"]
title: "A session past the cache TTL reads grey on the rail and leaves NEEDS YOU, so amber-pulse means waiting and still cheap to resume"
status: merged
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
source: ["user:edwin"]
commit: ""
pr: ""
impacts: ["desktop/src/renderer/cache-temperature.ts", "desktop/src/renderer/renderer.ts", "desktop/src/renderer/index.html", "desktop/tests/cache-temperature.test.mjs"]
issues: ["ISS-0105"]
features: ["FEAT-0081"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[FEAT-0081-What-A-Session-Costs-To-Keep-Alive]]", "[[ISS-0105-The-Rail-Pulses-The-Same-For-Two-Minutes-And-Two-Hundred-Hours]]", "[[CHG-20260806-Session-Cache-Economics]]"]
---

# A session past the cache TTL reads grey, and leaves NEEDS YOU

## Summary

The rail's amber pulse meant "the agent finished its turn — review it", with no notion of age. Measured on this machine: five of ten workspaces were pulsing amber at 1 min, 50h, 185h, 209h and 211h. A signal that is on for half the fleet permanently is decoration, and it was shouting loudest about exactly the sessions that cost most to resume — after an hour the prompt cache has lapsed, so picking one up re-writes the whole prefix ([[FEAT-0081]]).

Edwin's fix, which is better than the one originally proposed: **cold sessions read grey, and leave the NEEDS YOU list.** No third meaning is added to the rail — cold takes the same branch `decayed_from` already took to reach the grey dot — and amber-pulse gains a distinction it never had. NEEDS YOU now means *blocked on you **and** still cheap to pick up*, which on the measured fleet takes it from five entries to one.

An earlier draft annotated the cold rows with their resume cost instead. Dropping the rows entirely is simpler: one rule across both surfaces, and nothing to annotate.

## Impact

- **New:** `desktop/src/renderer/cache-temperature.ts` — `cacheTemperature(state, now, ttl)` → `warm` / `cold` / `unknown`, a global loaded as a plain script like `health-marks.js`. Pure, so the boundary is testable without a DOM.
- **Changed:** the rail square paints the grey `idle` dot when cold, and its tooltip says so with the age.
- **Changed:** `attentionEntries()` drops cold workspaces, so they leave NEEDS YOU.
- **New:** a 30s temperature tick. This is the load-bearing part — the transition has no event behind it, because the premise is a session where nothing is happening.
- **Unchanged:** every colour, animation and state class. Nothing new was added to the rail's vocabulary.

`unknown` deliberately does not paint: a square with no timestamp has told us nothing, and greying it would assert an age never measured (the ISS-0065 lesson). `busy` is never cold whatever its timestamp says.

## The bug the verification caught

Worth recording because it passed every test first.

The tick originally cached each workspace's last computed temperature and repainted on a change. Unit tests green, first end-to-end check green. The second cycle failed: the DOM is **also** repainted by inbound SSE events, so after cold → warm (event) → cold (time) the cache still read `cold`, the tick saw no change, and the dot stayed amber forever — the exact failure this work exists to prevent, reintroduced by the optimisation meant to make it cheap.

The fix is to compare against **what is painted** rather than what was last decided — read the square's classes and the panel's rendered row ids, repaint on disagreement. Self-healing by construction: the tick cannot hold a stale opinion about the screen because it asks the screen. Re-verified over three cold → warm → cold cycles.

The general lesson, which is not new here: a cache keyed on "what I last decided" is wrong whenever something else can also act on the thing being cached.

## Documentation Coverage (All Types Considered)

- features: updated — [[FEAT-0081-What-A-Session-Costs-To-Keep-Alive]] reopened for its second surface, then closed
- requirements: not-applicable
- tasks: new — TASK-0346, TASK-0347
- issues: new — [[ISS-0105-The-Rail-Pulses-The-Same-For-Two-Minutes-And-Two-Hundred-Hours]] (filed and fixed)
- tests: new — `desktop/tests/cache-temperature.test.mjs` (9 cases, boundary-crossing). **Known gap:** the tick's self-healing property is verified over CDP, not by a suite — see the follow-up below.
- workflows: not-applicable
- decisions: not-applicable — reusing the existing grey rather than minting a state needed no ADR; had a new colour or animation been added, it would have.
- risks: not-applicable
- changes: this note
- snapshot: updated — counters, items, focus, PHASE-007 reopened and re-closed

## Follow-ups

- [ ] **Independent review is owed** for this note and [[CHG-20260806-Session-Cache-Economics]] — neither has had one.
- [ ] **The tick has no regression test.** Proving it needs a DOM, and jsdom would contradict the standing decision in `tests/test_desktop_node_suite.py` against bringing a JS test framework into a Python project. If the self-healing comparison regresses, nothing will fail. Worth revisiting if a second time-driven repaint ever appears.
- [ ] **A blocked session now disappears from NEEDS YOU after an hour**, leaving only the grey square. Intended — a list that never forgets is what was fixed — but it is a lost nag. If work is ever dropped because of it, the answer is a separate stale-obligations surface, not putting them back.
- [ ] `CACHE_TTL_MS` in the renderer duplicates `TTL_1H` in `session_cache.py`. Duplicated deliberately (the rail must decide for ten workspaces without ten sidecar round-trips, and when no sidecar is running) but nothing detects them drifting apart.
