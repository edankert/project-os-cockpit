---
type: "[[feature]]"
id: FEAT-0126
aliases: ["FEAT-0126"]
title: "A rendered mark is a check mark on every surface, whatever the file stores"
status: doing
owner: user:edwin
created: 2026-08-18
updated: "2026-08-20"
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: approved
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

- [ ] The picker, the canceled-row styling and the gate tooltip all render glyphs.
- [ ] A guard fails on a raw mark word reaching any surface.

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
