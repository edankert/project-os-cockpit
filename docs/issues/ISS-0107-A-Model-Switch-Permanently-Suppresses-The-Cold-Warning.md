---
type: "[[issue]]"
id: ISS-0107
aliases: ["ISS-0107"]
title: "Once the last turn switched model, the strip says `model switch` forever and never says `cold` again — the feature's headline output is suppressed by an event already paid for"
status: fixed
phase: ""
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
source: ["review:independent-2026-08-06"]
severity: medium
component: "renderer"
related: ["[[FEAT-0081-What-A-Session-Costs-To-Keep-Alive]]", "[[ISS-0104-Model-Switch-Discards-The-Warm-Cache]]", "[[CHG-20260806-Session-Cache-Economics]]"]
tests: []
---

# A model switch permanently suppresses the cold warning

## Problem

`renderAgentStripCache` treats `model_switch` as outranking the state word:

```ts
if (cache.model_switch) {
  label = `model switch · ${approxUsd(sw.cost_usd)}`;
  title = `Switching ${sw.from} → ${sw.to} discarded …`;
}
…
agentStripCache.dataset.cache = cache.model_switch ? 'cold' : cache.state;
```

The comment justifies it — "the cost is already paid" — and for the minutes after a switch that is right. But `model_switch` is derived from *the last turn in the transcript*, and it does not decay. A session left alone after a switch keeps that badge indefinitely: `warm`, `cooling 12m` and `cold` are never rendered again for the life of that transcript.

Two effects:

1. **A cold session never reads cold.** FEAT-0081's acceptance says "Given a cold live session, the strip names the estimated cost of the next turn's re-write" and "the strip shows … one of `warm` / `cooling <n>m` / `cold`". After a switch, neither holds. The dollar figure happens to be numerically identical (`sw.cost_usd` and `resume_cost_usd` are both `prefix × price × 2.0`), so the *cost* survives; the *state* does not, and the state is what ISS-0105 then acts on elsewhere.
2. **A warm session is painted in the cold colour.** `data-cache="cold"` forces `--severity-high` + bold two minutes after a switch, when the cache is warm and the next turn is cheap. The CHG says "Only the cold and cooling states take colour; a badge that is always lit stops being read" — this is the path that lights it permanently.

## Repro

Verified 2026-08-06 against the reader:

1. Transcript whose last turn switched model and re-wrote 610k tokens.
2. `live_state(path, now=+3min)` → `state: "warm"`, `model_switch` present → strip renders `model switch · ~$6.10` in the cold colour.
3. `live_state(path, now=+3h)` → `state: "cold"`, `model_switch` **still present** → strip still renders `model switch · ~$6.10`. The word `cold` never appears.

## Expected

The switch announcement is a *recent event*, so it should expire like one — shown while the switch is the freshest thing to say (a few minutes, or until the next turn), then giving way to the standing warm/cooling/cold state. Alternatively the two are separate facts and belong in separate spans; the strip already carries several.

## Actual

Sticky until the session takes another turn.

## Notes

Compounded by [[ISS-0106]]: a false `<synthetic>` switch is sticky in exactly the same way, so a connection reset can silence the cold warning for a session permanently.

## Next Actions

- [x] Decide whether the switch line expires on a clock or on the next turn
- [x] Ensure the standing state word is reachable in every case
- [x] A guard over `renderAgentStripCache` — it currently has none (see [[ISS-0110]])
