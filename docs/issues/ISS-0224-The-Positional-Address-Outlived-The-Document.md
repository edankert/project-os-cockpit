---
type: "[[issue]]"
id: ISS-0224
aliases: ["ISS-0224"]
title: "`section:` and `ordinal:` are a positional address for a document that no longer exists — and `(tier, note_id)` reproduces the suite order exactly in all three repos"
status: fixed
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
severity: medium
component: acceptance
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]]", "[[ISS-0219-Two-Checks-Claiming-One-Address]]", "[[ADR-0037-A-Verdict-Is-An-Event]]", "[[ISS-0222-The-Left-Pane-Groups-By-Tier-And-Nothing-Else]]"]
---

# `1.6.150` is where a check *was*, not what it *is*

Edwin, 2026-08-19: *"Why are we storing these arbitrary numbers #.#.# for the tier1/tier2 items? We can probably do away with this information. And just have the tst identifier instead?"*

**He is right, [[ADR-0030]] already said so, and the removal is measurably free.**

## What these fields are

`section: "1.6"` and `ordinal: 150` are the check's position in `ACCEPTANCE_TESTS.md` — the single document every suite used to be. `Item.number` renders them as `1.6.150`.

**That document does not exist in any migrated repo.** It was deleted at migration, deliberately, because a left-behind copy is the dual-source trap this project has paid for twice.

## ADR-0030 decision 4 already retired the concept

> *"`section:`/`area:`/`ordinal:` order the view; ordinal is display-only and sparse, so mid-section inserts stop shifting anything — **which retires the shifting section-ordinal address for good**."*

The *address* was retired. The *fields* were kept to order the view, and then kept ordering the view for two further migrations without anybody asking whether they still had to.

**[[ISS-0219]] is what that costs.** A check authored outside the migration has neither field, so `Item.number` rendered `.0` — and two such notes were two checks claiming one address. The fix made `number` fall back to `note_id`, which is this issue in miniature: the id was already the better address, applied only where the position was missing.

## Measured 2026-08-19, and this is the whole argument

**Sorting by `(tier, note_id)` produces byte-identical order to `(tier, section, ordinal, note_id)` in all three repos** — `project-os-cockpit` 34 items, `your-trainer` 581, `your-sudoku` 56. Not similar; identical, first row to last.

That is not luck. The migration allocated ids in document order, so the id *encodes* the position it replaced — and unlike the position, it does not change when something above it moves.

**And `area` is a complete grouping key on its own:** areas spanning more than one section — **0** in every repo (21/21, 77/77, 20/20). `section` adds nothing to the grouping either.

## Suggested fix

1. **`sort_items` keys on `(tier, note_id)`.** One line, and the order does not move.
2. **Group on `area` alone** — `view_payload`, `_acceptance_tier_groups`, the generated page. This is also what [[ISS-0222]] needs, so the two land together.
3. **`Item.number` becomes `note_id`, unconditionally**, and the `.0` fallback goes with the fields that caused it.
4. **The fields leave `test.md`, `SCHEMAS.md` and the validator** — upstream first, and refused **only in a repo that keeps ledgers**, the same conditional [[ADR-0037]] used so the eight unmigrated repos keep working.
5. **`migrated_from:` is untouched and is the answer to "where did this come from".** It already carries the pre-migration address *and the sha* — `tests/ACCEPTANCE_TESTS.md#1.1.1 @ 7de1a86` — so provenance survives without a live field pretending to be a current address. That distinction is the point: one is a record of the past, the other is a claim about the present.

## What to check before doing it

- **The file-shape parser keeps writing them.** `acceptance.parse` derives `section`/`ordinal` from row grammar, and `suite_at` reads twelve historical tags that still hold that shape. Those are facts about the past and must keep working — this is removal from the **note schema**, not from the parser.
- **`_section_key` and the delta.** Anything keying a historical comparison on `number` needs re-checking against the id, the same sweep [[ISS-0219]] did for one consumer.

## Done when

- [x] `sort_items` reads `(tier, note_id)`, proved order-identical on all three repos.
- [x] Nothing groups on `section`.
- [x] `Item.number` is the note id.
- [x] The fields leave the schema and template, upstream first, refused only where a ledger exists.
- [x] `suite_at` still reads the twelve pre-migration tags.
