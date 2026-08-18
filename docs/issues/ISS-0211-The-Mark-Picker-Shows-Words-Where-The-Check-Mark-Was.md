---
type: "[[issue]]"
id: ISS-0211
aliases: ["ISS-0211"]
title: "The mark picker renders `[done]` where it used to render `[x]`, and two more sites lost their glyph when marks became words"
status: open
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
severity: medium
component: cockpit-desktop
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[ISS-0200-Marks-Versus-Statuses]]", "[[FEAT-0126-A-Rendered-Mark-Is-A-Check-Mark]]", "[[ADR-0034-Three-Axes-Not-One-Word]]"]
---

# A regression from ISS-0200, in the three places that bypass `MARK_GLYPH`

Edwin: *"I just noticed that you changed the checks in the Acceptance tests view to also use the states like done incomplete etc ... instead of using the check marks, this is where I would like to see the check marks and not the states."*

**He is right and the words are storage, not display.** [[ISS-0200]] changed `mark:` from characters to words in 669 notes, deliberately. What it also changed, without anybody noticing, is three render sites that read `mark` directly instead of going through `MARK_GLYPH`.

## The three sites

| site | before | now | effect |
| --- | --- | --- | --- |
| `renderer.ts:2341` — mark picker token | `[x]` `[/]` `[-]` `[!]` `[?]` `[ ]` | `[done]` `[incomplete]` `[canceled]` … | The dialog reads **"[done] Done — walked and passed"**: the word in brackets, beside a label that already says it |
| `renderer.ts:8524` — canceled row styling | `item.mark === '-'` | never true | **canceled rows silently lost their strikethrough** |
| `renderer.ts:4569` — gate row tooltip | `TST-0123 — [x]` | `TST-0123 — done` | a word where the glyph was |

The row rendering itself was fine throughout — it goes through `MARK_GLYPH`, which maps `done → [x]` and already handles the legacy characters.

## Why nothing caught it

Nothing asserts that a rendered mark is a glyph. The vocabulary migration was guarded on the *model* — `normalise_mark`, the validator, the payload — and the surfaces were re-keyed by hand. Two of the three sites do not even fail visibly: 8524 is a dead comparison, and 4569 is a `title` attribute.

This is the second time in two phases that a live surface kept a stale key after a vocabulary change; the first was `MARK_MEANING` reading *"unrecognised · 33"* in all three suites.

## Done when

- [ ] All three sites render through `MARK_GLYPH`.
- [ ] A guard fails if any surface emits a raw mark word — not a re-key by hand a third time.
