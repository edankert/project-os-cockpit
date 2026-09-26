---
type: "[[issue]]"
id: ISS-0115
aliases: ["ISS-0115"]
title: "[[ISS-0110]]'s repro still reproduces — deleting all three call sites leaves the suite fully green, greener than before, while the change note says it now turns red"
status: fixed
phase: ""
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
source: ["review:independent-2026-08-06-round-2"]
severity: medium
component: "tests"
related: ["[[ISS-0110-The-Whole-Cold-Reads-Grey-Behaviour-Can-Be-Reverted-With-A-Green-Suite]]", "[[TASK-0351-Pure-Decisions-For-The-Rail-And-The-Badge]]", "[[CHG-20260806-Review-Findings-Fixed]]"]
tests: []
---

# ISS-0110's repro still reproduces

## Problem

The fix for [[ISS-0110]] is the right one and it works: `railKey`, `attentionIds` and `cacheBadge` are pure, live in the plain-script module, and every mutation aimed at them dies (verified independently — see Evidence). The **claim** made for it does not hold.

[[CHG-20260806-Review-Findings-Fixed]] says:

> `railKey`, `attentionIds` and `cacheBadge` join `cacheTemperature` in the plain-script module the node suite can evaluate, **so deleting ISS-0105's behaviour now turns the suite red**.

Thirty lines later the same note says the opposite, correctly:

> The DOM adapters themselves are still unguarded — a much smaller surface than before, but not zero.

The second sentence is the true one, and the first is the one a reader takes away, because it is the one in the section headed "The guards".

## Repro (2026-08-06, independent re-review)

[[ISS-0110]]'s original repro, run verbatim against `HEAD` = `4de65a3`. All three call sites removed from `desktop/src/renderer/renderer.ts`:

1. `const key = railKey(state, Date.now()) || state.state;` → `const key = state.state;`
2. `if (!eligible.has(wsId)) continue;` → deleted
3. `window.setInterval(tickTemperatures, 30_000);` → deleted

`npm run build` compiles clean (no unused-local error), and:

```
.venv/bin/pytest -q
783 passed, 2 skipped
```

— where the second skip is `test_release.py` declining to run on a dirty tree, i.e. **784 passed / 1 skipped on a clean tree: fully green**. This is *better* than the previous round, which at least reported `1 failed` on `test_desktop_build_is_not_stale`; rebuilding after the revert clears even that. The rail no longer greys, NEEDS YOU no longer sheds cold entries, nothing ticks, and no test says so.

`grep -rn "railKey\|attentionIds\|cacheBadge\|applyAgentStateToSquare\|attentionEntries\|tickTemperatures" tests/ desktop/tests/` matches nothing outside `desktop/tests/cache-temperature.test.mjs`.

## A second, concrete piece of it: the tick never became an adapter

[[TASK-0351]]'s Definition of Done ticks:

> - [x] The three call sites become one-line adapters …

Two did. The third, `tickTemperatures` (`renderer.ts:12408`), is untouched and still decides the rule itself:

```ts
const cold = cacheTemperature(state, now) === 'cold';
const painted = li.classList.contains('state-idle');
const shouldBeIdle = cold || !!state.decayed_from || state.state === 'idle';
```

That is `railKey`'s rule, re-implemented inline. There are now **two** copies of one decision, one tested and one not, and they are free to drift: any state `railKey` learns to exempt, `shouldBeIdle` will not — and the tick would then repaint on every pass, or never.

## Expected

Either the claim narrowed to what the guards cover, or the last mile closed. The cheapest honest version of the second: `tickTemperatures` calls `railKey(state, now) === 'idle'` instead of recomputing it, which removes the duplicate decision without a DOM test.

## Actual

A good fix, described as a complete one, with the issue's own repro still working and one of its three named call sites untouched.

## Evidence

Mutations run against the built module, each restored afterwards — all six die, so the pure functions are genuinely guarded:

| mutation | result |
|---|---|
| `railKey`: drop the cold demotion | killed |
| `railKey`: drop the `decayed_from` branch | killed |
| `attentionIds`: drop the cold filter | killed |
| `attentionIds`: drop the `decayed_from` filter | killed |
| `cacheBadge`: tone borrows `cold` on a switch | killed |
| `cacheBadge`: drop the switch label entirely | killed |

## Next Actions
- [x] Correct the sentence in [[CHG-20260806-Review-Findings-Fixed]] and the ticked DoD in [[TASK-0351]]
- [x] Make `tickTemperatures` call `railKey` rather than restate it
- [x] Decide whether "the adapters are unguarded" is a permanent accepted gap and record it once, rather than in three notes with three widths
