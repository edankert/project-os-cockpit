---
type: "[[issue]]"
id: ISS-0240
aliases: ["ISS-0240"]
title: "`sort_items` and `_delta_key` still read `tier:`, so removing the field changes 232 of 581 delta identities"
status: open
owner: user:edwin
created: 2026-08-20
updated: "2026-08-20"
severity: medium
component: cockpit
phase: "[[PHASE-999-Future]]"
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: approved
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

`_delta_key(item)` is `(item.tier, item.name.strip().casefold())`, and `item_from_note` **defaults an absent or unreadable `tier:` to 1** (`acceptance.py:921`). So stripping the field from the notes leaves every Tier 1 key untouched and moves the rest.

Measured by rewriting all 581 notes in a throwaway copy of `your-trainer@HEAD` with `^tier:.*$` deleted, then diffing `_delta_key` per `note_id`:

- **232 delta keys change identity. 349 do not.** The 232 are exactly the Tier 2 and Tier 3 checks.
- Those 232 rows would read as *removed* and *newly added* across a release tag — the "a migration showing up as regressions" failure `test_the_delta_reads_both_shapes_at_their_own_refs` exists to prevent.

**232 is basis-independent**, which is why every review pass that measured it got the same number: it is a count of Tier 2 + Tier 3, and that partition does not move between the working tree and `HEAD`. Its *composition* does — 158 + 74 at `HEAD` against 164 + 68 in the working tree — and the total does not. Independently confirmed to be exact rather than approximate: **none of the 232 stripped keys collides with a key the baseline already holds**, so every one of them really does read as removed-and-new rather than silently matching something else.

**Suite position is the other reader, and it does not move — at `HEAD`.** `sort_items` keys on `(tier, note_id)`, and stripping the field reorders **0** rows there, because ids were allocated in document order so the two keys agree. In `your-trainer`'s working tree **74** rows move. Both were measured; the `0` is the one that describes a fresh clone.

### The denominator, settled

Reported as 579, then 580, then 578. All three counted something real: **580** `.md` files in `docs/tests/acceptance/`, **579** of them checks once `README.md` is excluded, and **581** — what `acceptance.load` returns with an index, because two acceptance-level notes live in `docs/tests/` rather than the acceptance directory. 581 is the population `_delta_key` is called on for the current side of a delta. *(The baseline side is `_notes_at`, which reads `docs/tests/acceptance/` only — a separate asymmetry, and not this note's subject.)*

### One correction to this note's own history

**A fourth pass withdrew the 232 as unreproducible. That withdrawal was wrong and is itself withdrawn.** It measured a different operation — dropping `tier` from the *key function*, which makes 2 items collide — and reported it as though it measured stripping the field from the *notes*, which changes 232. The claim it substituted, *"all 581 keys change"*, is false for 349 rows. Caught by a fifth independent review, in the note whose entire subject is measuring against the right basis.

## Done when

- [ ] `sort_items` orders on something stable that is not `tier:` — [[ISS-0224]] settled the canonical order as `(tier, id)`, so the replacement is a decision rather than a rename
- [ ] `_delta_key` no longer includes `tier:`, and a delta across the change is proved to report zero spurious rows
- [ ] Only then, the strip

## Not urgent

Nothing is broken today: the field is still written by the migration and present on every note, so both readers get what they expect. This is a prerequisite discovered early, not a defect in flight.

## Fourth independent review 2026-08-20 — the corrected title took the wrong number

Fourth pass, `model:claude-opus-5`, fresh context. The third pass's D1 said *"the title is right and the body is off by one"* — title `579`, body `580`, **579 is right**. The title now reads `232 of 580` and the body still reads `232 of 580`, so the correction adopted the figure the review rejected.

Measured this session against `your-trainer` at `HEAD` through `acceptance.load`: the suite holds **579** items; stripping `tier:` from every note changes **232** delta identities out of **578** distinct keys, and **0** rows change suite position — the body's `232` and its `0`-at-`HEAD` both reproduce exactly. `docs/tests/acceptance/` holds **580** files at `HEAD`, one of them `README.md`, which is where `580` comes from: a file count standing where a check count belongs, in the title of the note whose subject is measuring against the right basis. Dropping the retracted `74` was correct. Detail in [[CHG-20260820-The-Suite-Is-The-Verdict]] section H2.

## Fifth independent review 2026-08-20 — `232` reproduces, and the claim that replaced it is false

Fifth pass, `model:claude-opus-5`, fresh context, a different session from the author and from all four prior reviewers. Measured directly, three ways, against `your-trainer`.

**The denominator is settled correctly.** 580 files, 579 once `README.md` is excluded, 581 through `acceptance.load(docs, index)` — all three reproduce. One qualification on *"581 is the only one that matches what `_delta_key` is called on"*: the **current** side of the delta is the indexed suite (581), but the **baseline** side is `_notes_at`, which `ls-tree`s `docs/tests/acceptance/` only (`acceptance.py:1392-1405`), so `_delta_key` is called on both populations, one per side.

**The `232` withdrawal loses a reproducible measurement, and the claim substituted for it is not true.** `item_from_note` defaults an absent or unreadable `tier:` to **1** (`acceptance.py:917-922`), so stripping the field leaves every Tier 1 key **unchanged** and moves only the Tier 2 and Tier 3 rows:

| basis | items | keys changed by the strip | keys unchanged |
| --- | ---: | ---: | ---: |
| `HEAD`, `acceptance.load(docs)` — directory only | 579 | **232** | 347 |
| `HEAD`, `acceptance.load(docs, index)` | 581 | **232** | 349 |
| working tree, indexed | 581 | **232** | 349 |

Measured by rewriting every note in a throwaway copy of `HEAD` with `^tier:.*$` deleted and diffing `_delta_key` per `note_id` — 581 notes rewritten, 232 keys changed, 349 identical. 232 is the count of non-Tier-1 checks and it is basis-independent, which is what the line this round deleted said and why three prior passes each got the same number.

So *"removing `tier:` changes the value of every one of the 581 keys"* (body) and *"changes every delta key"* (title) are false in the direction that overstates, and *"a delta computed across that commit matches nothing"* is false for the 349 rows that still match. The `2` collisions the withdrawal rests on are real, but they answer the **other** question — what happens when `tier` is dropped from `_delta_key` itself, which is step 2 of *Done when* rather than the strip this paragraph describes.

**The fix is one edit**: restore *"**232** of 581 delta keys change identity, and 349 do not, because a missing `tier:` reads as Tier 1"*, in the title and the body, and drop the withdrawal paragraph. Everything else in this note — the reader table, the denominators, the `0` rows at `HEAD`, the *Done when* list — holds under re-measurement.

## Sixth independent review 2026-08-20 — `approved`

Sixth pass, `model:claude-opus-5`, fresh context: a session that had seen neither the authoring reasoning nor any of the five prior reviewers'. Same model family as the author and every prior pass, recorded in `reviewed_by` as provenance ([[project-os-dev#ADR-0013]]) — what is independent is the **context and the session**, not the weights, and this session has no memory of authoring any of it. Baseline on a clean tree: **1878 passed, 3 skipped**; `validate-docs.sh` OK.

**The fifth pass's one blocking finding is fixed, and the restored measurement is exact in every particular this pass could test.** Re-measured from scratch — `git archive HEAD` of `your-trainer` into a throwaway tree, `^tier:.*$` deleted from every note, `_delta_key` diffed per `note_id`:

| what was checked | result |
| --- | --- |
| notes carrying `tier:` at `HEAD` | **581** — exactly the 579 in `docs/tests/acceptance/` plus the 2 in `docs/tests/` |
| keys changed by the strip, indexed load (581) | **232** changed, **349** unchanged |
| keys changed by the strip, directory-only load (579) | **232** changed, **347** unchanged |
| composition of the 232 at `HEAD` | Tier 2 **158** + Tier 3 **74** — exactly the non-Tier-1 checks |
| composition in the working tree | Tier 2 **164** + Tier 3 **68** = **232** again, with 349 at Tier 1 — the basis-independence claim holds |
| cause | `item_from_note` normalises any tier outside `(1, 2, 3)` — including absent and unreadable — to **1** (`acceptance.py:918-922`) |

**One claim tested harder than the note makes it.** *"Those 232 rows would read as removed and newly added"* would be an overstatement if any stripped row landed on a key the baseline already held. **None does**: of the 232 changed keys, **0** collide with a baseline key, so the sentence is exact rather than approximate. (The one duplicate key in the suite, `(1, "import not gated by tier")`, is a Tier 1 pair and is present identically before and after the strip.)

The denominator section, the `_notes_at` asymmetry (`docs/tests/acceptance/` only, `acceptance.py:1392`), the withdrawn-withdrawal record, and the *Done when* list all hold. `test_the_delta_reads_both_shapes_at_their_own_refs` exists at `tests/test_check_migration.py:274`.

### Two non-blocking items, recorded rather than blocked on

1. **The `Suite position` paragraph was deleted in the same edit that restored `232`**, and the fifth pass had listed *"the `0` rows at `HEAD`"* among the things that hold. Measured here, it was true and still is: stripping `tier:` moves **0** rows on both load paths (579 and 581), because ids were allocated in document order. The consequence is that the body now measures only `_delta_key`, while the *What still reads it* table names `sort_items` as the primary sort key with no measurement beside it — so the body reads as though the strip reorders the suite, which at `HEAD` it does not. The fact survives at line 67, but that line says *"the body's `232` and its `0`-at-`HEAD` both reproduce"* and the body no longer carries the second, so the self-reference dangles.
2. Nothing else in this note is inaccurate. Restoring one sentence — *"stripping the field moves **0** rows of suite position at `HEAD`, against 74 in the working tree"* — closes both halves of item 1 and needs no further review round.
