---
type: "[[issue]]"
id: ISS-0240
aliases: ["ISS-0240"]
title: "`sort_items` and `_delta_key` still read `tier:`, so removing the field changes every delta key and cannot be done without replacing them"
status: open
owner: user:edwin
created: 2026-08-20
updated: "2026-08-20"
severity: medium
component: cockpit
phase: "[[PHASE-999-Future]]"
related: ["[[ADR-0039-Three-Sections-Derived-Not-Filed]]", "[[ISS-0208-Retire-The-Tier-Rule]]", "[[PHASE-039-A-Test-Says-Who-Executes-It]]", "[[CHG-20260820-The-Suite-Is-The-Verdict]]"]
---

# The field is unread where it decides, and read where it orders

[[PHASE-039]] closed on a criterion reading *"`tier:` is read by no code path"*. That is false, and independent review caught it.

**What is true**: no *section* and no *gate* decision reads `tier:`. `GATING_TIERS`, `PERMANENT_TIERS` and `TIER_LABELS` are deleted, and `blocking_for`, `missing_issue_refs` and both front doors read `section_of` instead.

**What still reads it**:

| site | what it uses the field for |
| --- | --- |
| `acceptance.sort_items` | the primary sort key — a check's canonical position in the suite |
| `acceptance._delta_key` | part of a row's IDENTITY across two release tags |
| `Suite.tier` | kept for the file-shape parser, which derives a tier from a document heading |
| `tools/scripts/migrate-acceptance-checks.py` | writes `tier:` into migrated notes and scopes its parity comparison |

## Why this matters, measured

`_delta_key(item)` is `(item.tier, item.name.strip().casefold())`. Removing `tier:` therefore changes **the value of every one of the 581 keys** in `your-trainer` at `HEAD`. A release delta computed across the commit that strips the field compares old keys against new ones and matches nothing: every check reads as *removed* and *newly added*, once.

### The denominator, settled

It was reported as 579, then 580, then 578 across three review passes. **All three counted something real and none counted the same thing:**

| | |
| --- | ---: |
| `.md` files in `docs/tests/acceptance/` | 580 |
| …minus `README.md` | 579 |
| acceptance-level notes **outside** that directory, in `docs/tests/` | **2** |
| **what `acceptance.load` actually returns, and what the code operates on** | **581** |

580 was a file count. 579 was the directory minus its README. 581 is the population, and it is the only one of the three that matches what `_delta_key` is called on.

**The `232` figure is withdrawn rather than picked.** Re-measured directly: dropping `tier` from the key makes exactly **2** items collide — two checks share a casefolded name across different tiers. I cannot reproduce 232 by any reading and will not assert a number I cannot get twice. It is also unnecessary: the claim above is stronger, simpler and certain.

**Suite position**: 74 rows move — *in the working tree*. At `HEAD` **zero** move, because ids there were allocated in document order, so `(tier, id)` and `(id)` agree. This note was filed to correct a working-tree measurement and repeated one; caught by a second independent review.

## Done when

- [ ] `sort_items` orders on something stable that is not `tier:` — [[ISS-0224]] settled the canonical order as `(tier, id)`, so the replacement is a decision rather than a rename
- [ ] `_delta_key` no longer includes `tier:`, and a delta across the change is proved to report zero spurious rows
- [ ] Only then, the strip

## Not urgent

Nothing is broken today: the field is still written by the migration and present on every note, so both readers get what they expect. This is a prerequisite discovered early, not a defect in flight.

## Fourth independent review 2026-08-20 — the corrected title took the wrong number

Fourth pass, `model:claude-opus-5`, fresh context. The third pass's D1 said *"the title is right and the body is off by one"* — title `579`, body `580`, **579 is right**. The title now reads `232 of 580` and the body still reads `232 of 580`, so the correction adopted the figure the review rejected.

Measured this session against `your-trainer` at `HEAD` through `acceptance.load`: the suite holds **579** items; stripping `tier:` from every note changes **232** delta identities out of **578** distinct keys, and **0** rows change suite position — the body's `232` and its `0`-at-`HEAD` both reproduce exactly. `docs/tests/acceptance/` holds **580** files at `HEAD`, one of them `README.md`, which is where `580` comes from: a file count standing where a check count belongs, in the title of the note whose subject is measuring against the right basis. Dropping the retracted `74` was correct. Detail in [[CHG-20260820-The-Suite-Is-The-Verdict]] section H2.
