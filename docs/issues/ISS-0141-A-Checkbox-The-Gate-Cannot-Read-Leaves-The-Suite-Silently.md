---
type: "[[issue]]"
id: ISS-0141
aliases: ["ISS-0141"]
title: "A checkbox whose mark the parser does not recognise leaves the suite silently — the release gate's denominator can shrink without anyone saying so"
status: fixed
severity: medium
owner: user:edwin
created: 2026-08-11
updated: 2026-08-11
phase: "[[PHASE-030-Obligations-Go-Home]]"
features: ["[[FEAT-0086-Tests-Becomes-A-View]]"]
tasks: []
related: ["[[REL-0001-The-Human-Has-Levers]]", "[[TASK-0373-The-Tier-Suite-And-The-Release-Gate]]", "[[ISS-0121]]"]
tags: [issue, gate, parser]
---

# A checkbox the gate cannot read leaves the suite silently

## What was found

Walking the last check of [[REL-0001]] on 2026-08-11, with the gate about to be reported green for the first time. `acceptance.py` parsed the suite:

```
tier 1: parsed 26, checked 26      # the document holds 27 items
tier 3: parsed 1,  checked 1       # the document holds 2
gate blocked False  blocking []
```

`_ITEM_RE` matched `^-\s+\[( |x|X)\]` — space, `x`, `X` and nothing else. **The record had invented a third mark** and used it twice: `- [~]`, *reconciled* — a check settled by a decision rather than by being walked (1.5.2, whose surface was retired eleven days before the suite was written; and 3.2, unwalkable by construction). Neither line matched, so neither became an `Item`. Not counted, not gating, not rendered, not mentioned.

**The outcome was right and the mechanism was not.** A reconciled check should not block a release — that is what reconciling means. But it reached that outcome by being *invisible*, and the same code path is indifferent to why a mark is unrecognised:

- `- [X]` is fine; `- [v]`, `- [-]`, `- [ x]` are all silently dropped.
- **One mistyped character removes a check from the gate**, and every surface then agrees the suite is complete.
- The Tests view read `Tier 1 · 26/26` — a full bar, over a document with 27 items.

That is the failure this project keeps naming: *a surface asserting something false about the record without saying so*. It is [[ISS-0121]]'s shape (settled work counted as owed) with the sign flipped — owed work counted as absent — and this one is load-bearing, because it feeds a release gate.

## Why it matters more than the two lines it affected

Nothing was actually mis-gated: both reconciled items carry their reasoning on the line, and REL-0001 records both. The defect is in what the gate **can** be told. A checklist whose parser drops what it does not recognise has no error state — every unreadable line reads as "nothing here", and the number goes up.

`tools/instructions/TESTING.md` never named this mark either, so the record and the contract had drifted apart in a place only a human reader could see.

## The fix

`acceptance.py` now matches **any** single-character mark and decides what it means:

- `x` / `X` → walked.
- `~` → **reconciled**: settled by a decision, does not block, and is *counted and named* rather than dropped.
- **anything else, including a blank → owed**, so it blocks.

The last clause is the one that matters: the parser no longer has a way to say nothing. An item it cannot classify is treated as unfinished, which is the direction that fails safely. `blocking()` reads `settled` (checked or reconciled) instead of `checked`, so the verdict is unchanged where the record was already right, and the payload carries a `reconciled` count so the Tests view can say `26/27 · 1 reconciled` instead of `26/26`.

## What the tests hold

`tests/test_tests_view.py`:

- A `[~]` item is **in** the tier, is not blocking, and is counted as reconciled — the case that used to vanish.
- An **unrecognised** mark blocks, named in `blocking` — the mistyped-checkbox case, which had no test because it had no behaviour.
- The live suite is not blocked, and every Tier 1/2 item is settled — replacing two assertions that encoded *"the gate is red today"*, which were true when written and became false the moment the gate went green. Their fixture-based twins (`test_an_unchecked_tier_one_test_blocks_and_checking_it_clears`) already prove the blocking direction, so nothing is lost by making the live-suite test assert the live truth.

## Owed upstream

The mark is this repo's invention; `TESTING.md` is template-owned and describes checked/unchecked only. Proposed upstream so a reconciled check means the same thing in every repo — until then this repo's parser understands one more state than the contract names, which is recorded here rather than left for the next reader to discover the way this one did.
