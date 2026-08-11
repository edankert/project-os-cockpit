---
type: "[[change]]"
id: CHG-20260811-Gate-Green
title: "The acceptance gate fires green for the first time — and the pass that closed it found the gate under-reporting its own suite"
status: merged
date: 2026-08-11
owner: user:edwin
related: ["[[REL-0001-The-Human-Has-Levers]]", "[[ACCEPTANCE-TESTS]]", "[[ISS-0141]]", "[[ISS-0140-The-Shell-Goes-Stale-Silently]]", "[[ISS-0139]]", "[[ISS-0142]]", "[[FEAT-0086-Tests-Becomes-A-View]]"]
tags: [change]
---

# The gate goes green

[[REL-0001]]'s last unwalked check fell, and closing it changed behaviour in three places. **34 of 34 Tier 1/2 items settled, 36 of 36 including Tier 3, no exception claimed.**

## What changed

**The acceptance parser reads every mark ([[ISS-0141]]).** `_ITEM_RE` matched `[ ]`, `[x]` and `[X]`; anything else — including `- [~]`, the record's own mark for a check settled by decision — was **not parsed as an item at all**. Not counted, not gating, not rendered. The verdict it produced was right and the mechanism was not: the same path drops a typo just as quietly, so one mistaken character removed a check from the gate and every surface then agreed the suite was complete.

Now: `x`/`X` walked, `~` **reconciled** (settled, does not block, counted and named), and **anything else owed**, so it blocks. The parser no longer has a way to say nothing.

**The Tests view stops rounding down.** `Tier 1 — feature tests · 26/26` over a 27-item document now reads `· 26/27 · 1 reconciled`, and a reconciled row carries `reconciled` rather than `ready` — settled, but not claiming it was walked.

**The release gate band stops overstating.** *"Release gate clear — every Tier 1 and Tier 2 test is checked"* is false when one was reconciled instead, and a clear gate is where an overstatement costs most, because nobody looks twice at a green light. It now names the count when there is one.

## Impact

- `GET /api/cockpit/acceptance` gains `reconciled` per tier and per item, and `counts.tierN.unchecked` now means *unsettled* rather than *unticked*. A consumer reading `checked` alone sees the same numbers as before.
- No release verdict changes: both reconciled items were already settled by decision in the record. What changes is that the surfaces can now say so.

## Documentation Coverage (All Types Considered)

- features: not-applicable
- requirements: not-applicable
- tasks: not-applicable
- issues: new ([[ISS-0141]], [[ISS-0142]]) · updated ([[ISS-0139]], [[ISS-0140]])
- tests: updated (`docs/tests/ACCEPTANCE_TESTS.md`, `tests/test_tests_view.py`)
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new (this note)
- snapshot: updated (focus, counters)

## What the pass cost, and why that is the point

Three findings came out of walking one checkbox, none of them visible to a 1159-test suite that was green throughout:

- **[[ISS-0141]]** — the gate under-reporting its own suite, found *on the day it first passed*.
- **[[ISS-0139]] corrected** — the issue said `/api/cockpit/changes` had no consumer and should be deleted with its dead function. The endpoint feeds the quick-switch palette; deleting it would have removed 126 change notes from the only surface that finds them by name. The dead function is real; the endpoint is load-bearing.
- **[[ISS-0142]]** — releases are the one note type the palette has never carried, so `REL-0001` typed into *"files, IDs, or commands"* returns nothing.

## Follow-ups

- [ ] [[ISS-0142]] is `triage` — releases need either a nav home or the third corpus patch beside changes and tests.
- [ ] The reconciled mark is this repo's invention; `TESTING.md` is template-owned and names checked/unchecked only. Propose it upstream.
