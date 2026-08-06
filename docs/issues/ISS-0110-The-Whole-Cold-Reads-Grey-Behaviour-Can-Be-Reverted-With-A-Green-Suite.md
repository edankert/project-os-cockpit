---
type: "[[issue]]"
id: ISS-0110
aliases: ["ISS-0110"]
title: "The entire ISS-0105 behaviour can be deleted and the suite stays green — the node tests guard the pure predicate, not any of the three call sites that are the fix"
status: triage
phase: ""
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
source: ["review:independent-2026-08-06"]
severity: medium
component: "tests"
related: ["[[ISS-0105-The-Rail-Pulses-The-Same-For-Two-Minutes-And-Two-Hundred-Hours]]", "[[TASK-0346-Cold-Reads-Grey-And-Actually-Ticks]]", "[[TASK-0347-Cold-Sessions-Leave-The-Needs-You-List]]", "[[CHG-20260806-Cold-Sessions-Read-Grey]]"]
tests: []
---

# The whole cold-reads-grey behaviour can be reverted with a green suite

## Problem

`desktop/tests/cache-temperature.test.mjs` is a good test of `cacheTemperature`, and it kills the mutations it was written for (the `>=` boundary, the busy exemption, a 60× TTL error, `unknown` → `cold`). But `cacheTemperature` is a **decision**, not the fix. ISS-0105's fix is three call sites in `renderer.ts`:

1. `applyAgentStateToSquare` — `const key = (state.decayed_from || cold) ? 'idle' : state.state;`
2. `attentionEntries` — `if (isColdWorkspace(state)) continue;`
3. `window.setInterval(tickTemperatures, 30_000)` and the painted-vs-wanted comparison inside it

## Repro (mutation testing, 2026-08-06)

All three were removed from `desktop/src/renderer/renderer.ts` simultaneously — reverting ISS-0105 entirely — and the full suite was run:

```
1 failed, 762 passed, 2 skipped
FAILED tests/test_status_vocabulary.py::test_desktop_build_is_not_stale
```

The single failure is an mtime comparison between source and `dist/`, which a rebuild clears. No behavioural test noticed that the rail no longer greys, the NEEDS YOU list no longer sheds cold entries, and nothing ticks. `grep -rl "tickTemperatures\|isColdWorkspace\|attentionEntries\|renderAgentStripCache" tests/ desktop/tests/` matches nothing outside `cache-temperature.test.mjs`.

`renderAgentStripCache` — the entirety of TASK-0344's and TASK-0345's user-visible output — has no test of any kind.

## What is already recorded, and what is not

TASK-0346 and TASK-0347 are honest about part of this: both say the CDP verification is not a suite, and TASK-0346's "Verification gap, recorded rather than papered over" is exactly the right instinct. So this is not a hidden gap; it is an **understated** one.

What is not recorded:

- The gap is described as the **tick's** self-healing property. It is in fact all three call sites, plus the strip renderer.
- TASK-0347's DoD ticks "The T+59min-present / T+61min-absent boundary is proven", with a parenthetical that the *list emptying* was CDP-only. The boundary is proven for `cacheTemperature`; the list's use of it is not proven at all, by any means that survives the session.
- `CHG-20260806-Cold-Sessions-Read-Grey`'s coverage line reads "tests: new — `desktop/tests/cache-temperature.test.mjs` (9 cases, boundary-crossing)" with the known gap named as the tick only. A reader takes that as coverage of the change.

The bug the change note proudly records — the temperature cache that made the dot stay amber forever — is precisely the class of bug none of these 9 tests can catch, and it was caught by a human running the cycle twice. Next time there may be no second cycle.

## Expected

Either a DOM-level guard for the three call sites, or the gap stated at its true width in the notes so no one reads the 9 green cases as coverage of the behaviour.

The standing decision against a JS test framework (`tests/test_desktop_node_suite.py`) is sound and should not be overturned casually. The middle path already used elsewhere in this repo is to push the decision further out of the DOM: a pure `railKey(state, now)` returning the class to paint, and a pure `attentionIds(states, now)` returning the ids the panel should show, both testable in the node suite, leaving the call sites as one-line adapters.

## Next Actions

- [ ] Extract the two call-site decisions into pure functions and guard them in the node suite
- [ ] Correct the coverage wording in the CHG and in TASK-0347's DoD
- [ ] Decide whether `renderAgentStripCache` gets the same treatment (see [[ISS-0107]])
