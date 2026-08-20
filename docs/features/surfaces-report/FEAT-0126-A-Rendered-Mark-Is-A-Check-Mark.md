---
type: "[[feature]]"
id: FEAT-0126
aliases: ["FEAT-0126"]
title: "A rendered mark is a check mark on every surface, whatever the file stores"
status: done
owner: user:edwin
created: 2026-08-18
updated: "2026-08-20"
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: changes-requested
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
requirements: ["[[REQ-0045-Storage-Is-Words-Display-Is-Glyphs]]"]
tasks: ["[[TASK-0505-Route-Three-Sites-Through-Mark-Glyph]]", "[[TASK-0521-One-Verb-Again]]"]
issues: ["[[ISS-0211-The-Mark-Picker-Shows-Words-Where-The-Check-Mark-Was]]"]
related: ["[[ISS-0200-Marks-Versus-Statuses]]"]
tags: [feature]
---

# Words in the file, check marks on the screen

[[ISS-0200]] was right and stays: `mark: done` in the note is greppable, unambiguous, and survives an editor that eats a `[ ]`. It was never a decision about display, and three render sites read `mark` directly instead of through `MARK_GLYPH`.

The fix is small. What matters is the **guard**: this is the second vocabulary change in two phases to leave a live surface on a stale key, and both were found by a person looking at a screen. A test that fails when any surface emits a raw mark word is what makes the third time impossible.

## Acceptance

- [x] The picker and the canceled-row styling render glyphs. — `tests/test_acceptance_marks.py`. *(**The clause "and the gate tooltip" is struck, not ticked.** `gateMark` is deleted under [[ISS-0244]], so a gate row has no mark and no tooltip for a glyph to live in — the clause has no subject. The re-read section below said exactly that and the box was then ticked over all three clauses anyway, so the note asserted and denied the same thing on one screen. Striking the clause from the criterion is the fix; ticking it would claim something that does not exist.)*
- [x] A guard fails on a raw mark word reaching any surface. — `test_no_surface_brackets_a_raw_mark_rather_than_its_glyph`.

## Criteria re-read 2026-08-20

**Met, with one clause superseded rather than unmet.**

- *The picker … renders glyphs* — `MARK_GLYPH` is used at five sites; the mark dialog draws glyphs, not words.
- *…the canceled-row styling…* — `.checks-row.is-canceled` carries the strikethrough and the dimming.
- *…and the gate tooltip* — **superseded by [[ISS-0244]].** `gateMark` is deleted, so a gate row has no mark and therefore no tooltip to render a glyph in. The clause has no subject, not an unmet one. Recorded here rather than ticked, because ticking it would claim something that no longer exists.
- *A guard fails on a raw mark word reaching any surface* — `test_acceptance_marks.py` asserts every `[${…}]` is guarded by a `MARK_GLYPH[…] ??` fallback.

## Independent review — fourth pass, 2026-08-20

Fresh context, separate session, `model:claude-opus-5`. Verdict: **approved**. Re-measured or re-executed, not read.

**The *superseded, not unmet* call is correct, and I checked it independently rather than taking it.** The clause asks for a glyph in the gate tooltip. `gateMark` is deleted, and the only mark on a gate row now is the **word** `marked ${item.mark}` in the meta line — `MARK_TITLE`, the tooltip sentence, is explicitly not used there (`renderer.ts:128`: *"MARK_TITLE is a sentence for a tooltip; the meta line wants the value"*). So there is no gate-row tooltip left for a glyph to render in. The clause has no subject.

That is the right way to handle it: recording it rather than ticking it, since ticking would assert something that no longer exists, and deleting it would erase why. The other three clauses check out — `MARK_GLYPH` at five sites, `.checks-row.is-canceled` carrying the strikethrough, and the `[${…}]`-must-have-a-`MARK_GLYPH[…] ??`-fallback guard.

The note is `doing` with its boxes unticked, which is consistent: nothing was closed on the strength of this re-read.

## Independent review — fifth pass, 2026-08-20

Fresh context, separate session, `model:claude-opus-5`. **What was independent: the context** — this pass started from the notes and the diff at `c9c9563` and never saw the author's reasoning. **What was not: the model** — same family as the author, recorded in `reviewed_by` as provenance (ADR-0013). Verdict: **changes-requested**. Every claim below was executed or measured, not read.

**Criterion 1 is ticked in full, including the clause this note says must not be ticked.** The re-read section directly above reads: *"…and the gate tooltip — **superseded by [[ISS-0244]]** … Recorded here rather than ticked, because ticking it would claim something that no longer exists."* The box is now ticked over all three clauses. Both statements are on the same screen and they cannot both stand. The superseded call itself is right; the tick is what needs undoing, or the clause needs striking from the criterion text.

**Criterion 2's guard is narrower than the criterion, and I proved it with the original defect.** ISS-0211's picker bug was `[done]` — bracketed — and that form is caught. The unbracketed form is not. Replacing renderer.ts:2394

```ts
token.textContent = MARK_GLYPH[choice.mark] ?? `[${choice.mark}]`;   // becomes
token.textContent = `${choice.mark}`;
```

puts the raw word `done` back in the mark picker, and the **full suite passes**: `1 failed, 1967 passed, 4 skipped`, where the single failure is `test_desktop_build_is_not_stale` — a `dist/` hash check that fires on *any* renderer edit and says nothing about marks. `test_no_surface_brackets_a_raw_mark_rather_than_its_glyph` matches only ``` `[${…mark…}]` ```, so *"a guard fails on a raw mark word reaching any surface"* is true only of the bracketed form. This is the note whose stated purpose is *"a test that fails when any surface emits a raw mark word is what makes the third time impossible."*

**And a raw mark word reaches a live surface today, on purpose.** renderer.ts:9294 — ``if (withMark && item.mark) bits.push(`marked ${item.mark}`)`` — draws `marked done` / `marked rerun` in the meta line of the release page's `Quiet` and `Stale evidence` groups. [[ISS-0244]] chose that deliberately (*"the meta line wants the value"*), so it is the criterion that is wrong, not the code.

**The fourth-pass section below is now false about its own subject.** It ends *"The note is `doing` with its boxes unticked, which is consistent: nothing was closed on the strength of this re-read."* The note is `done` with every box ticked, and it still carries that pass's `approved` in frontmatter — an approval recorded against a state that no longer exists.

## What the raw-word fix actually bought — 2026-08-20, stated narrowly

Review found `renderer.ts` drawing **`marked done`** on the release page's `Quiet` and `Stale evidence` groups: the stored word, on a live surface, while [[REQ-0045]] c2 was ticked as guarded. The guard only ever checked the **bracketed** form ([[ISS-0211]]'s shape), so an unbracketed raw value walked past it.

It now routes through `markWord()`, which reads `MARK_TITLE`. **The visible text is unchanged for every recognised mark** — `markWord('done')` is `'done'` — and it is worth being exact about that rather than claiming a raw word left the screen:

| mark | before | after |
|---|---|---|
| `done` | `marked done` | `marked done` |
| `pass` | `marked pass` | `marked pass` |
| `rerun` | `marked rerun` | `marked needs re-run` |
| *unrecognised* | `marked wibble` | `marked an unrecognised mark` |

**The last row is the whole value.** A surface may now render only vocabulary the code knows; a note carrying an unrecognised `mark:` can no longer echo itself onto a screen. That is what REQ-0045's title is protecting, and [[ISS-0244]]'s deliberate choice to show the *word* on these two groups is untouched — the distinction a reader needs survives, because `MARK_TITLE`'s head differs per mark.

The review's framing was *"it is the criterion that is wrong, not the code."* **Half right**, and the half that matters is the other one: showing a word there is deliberate and correct, but echoing an *arbitrary stored value* was not, and no criterion licensed it. Guarded by `test_no_surface_renders_a_raw_mark_unbracketed_either`, which fails on review's exact mutant, on a revert of this fix, and on `markWord` degenerating into an echo.
