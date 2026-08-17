---
type: "[[issue]]"
id: ISS-0186
aliases: ["ISS-0186"]
title: "The mark glyphs are decorative symbol characters and the dialog is too narrow for six two-line buttons"
status: "fixed"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
source: ["Edwin 2026-08-17, from use: 'I don't like the design of the tick, keep the font simpler and the dialog seems to small for all the buttons.'"]
severity: low
component: desktop-renderer
parent: ""
related: ["[[ISS-0185-The-Mark-Control-Sits-Inside-Tasklists-Leftover-Box-And-The-Cycle-Makes-You-Walk-Past-States]]", "[[ADR-0029-The-Acceptance-Mark-Vocabulary-Is-Minimals]]"]
tests: []
---

# The glyphs are decorative and the dialog is too narrow

Second round of feedback on the same control, both visual.

## 1. The glyphs

`○ ✓ ◐ – ! ?` — three of the six are geometric symbol characters that fall back to whatever font on the system happens to carry them, at a size chosen to make them legible. They read as decoration rather than as the marks they represent.

**They should be the marks themselves.** `[ ]` `[x]` `[/]` `[-]` `[!]` `[?]`, in the monospace face the rest of the app already uses for ids and paths. What is on screen is then exactly what is in the file — which is not only simpler but teaches the syntax, so a reader who edits the Markdown by hand already knows what to type.

## 2. The dialog

Six options, each a two-line button (label plus what it does to the gate), in a two-column grid at `max-width: 34rem`. The hints wrap, the columns fight, and the whole thing is cramped.

Six is too many for columns. A single column, one row per option, gives each hint its line and reads as a list of consequences — which is what it is.

## Expected

- The control shows the literal mark in the app's monospace face, at body size, no border.
- The dialog is a single column, wide enough that no hint wraps.
- Colour and weight keep carrying the state; nothing about the vocabulary or the write path changes ([[ADR-0029]]).

## Fixed 2026-08-17

**The control shows the mark.** `[ ]` `[x]` `[/]` `[-]` `[!]` `[?]`, in the monospace face the app already uses for ids and paths, at body size, no border. `○ ✓ ◐` are gone — they fell back to whatever font the system carried them in, and they were sized up to compensate, which is what made them read as decoration.

Showing the literal has a second benefit that was not the reason for the change but is the better argument for it: **what is on screen is what is in the file**, so a reader who edits the Markdown by hand has already seen what to type. A legacy `[~]` or `[F]` row shows its own character, because that is what is written there.

**The dialog is one column at 44rem.** Six two-line options in a two-column grid at 34rem wrapped every hint and fought for width. Each option is now a row — mark, label, consequence — which is what a list of consequences should look like. Each choice shows its mark, so picking `[!] Important` and then seeing `[!]` on the row is the same language twice.

Five mutations, all killed: restore a symbol glyph, drop the mono face, return to two columns, narrow the card, and stop showing marks in the dialog.

**The last of those survived the first time**, and the reason is worth keeping: the guard asserted the mark token was *created* and not that it was *appended*, so a mutation that built it and never attached it passed. Creating a node is not showing it.
