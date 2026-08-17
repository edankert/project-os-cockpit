---
type: "[[task]]"
id: TASK-0456
aliases: ["TASK-0456"]
title: "A checkbox carries its address, not its position — the write resolves a check number or refuses"
status: done
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["[[ISS-0184-Clicking-A-Checkbox-In-The-Acceptance-Suite-Writes-To-A-Different-Row]]", "[[FEAT-0104-The-Suite-Is-The-Surface]]"]
parent: "[[FEAT-0104-The-Suite-Is-The-Surface]]"
effort: M
depends: []
blocks: ["[[TASK-0435-The-Cycling-Mark-And-Its-Paired-Write]]"]
related: ["[[ISS-0175-The-Nth-Checkbox-Is-Not-The-Nth-Task-Line]]", "[[FEAT-0103-The-Gate-Is-Walkable]]"]
tests: []
---

# A checkbox carries its address

## Why

`check-toggle` addresses a box by its **ordinal among rendered checkboxes** and the server finds the Nth **source** token. Those agree only while every source box renders. `../your-trainer`'s suite has 579 source boxes and 542 rendered ones, so from index 257 the write lands on the wrong row and reports `ok` ([[ISS-0184]], reproduced).

[[FEAT-0103]] already refused to build the walker on this endpoint and recorded why: *"a walker addressed by global checkbox index would write to whichever row had moved into that position."* That reasoning was never applied back.

## What

`renderer._annotate_checkbox_source` already walks the rendered boxes against the source. It gains a second attribute — the check's **address** (`1.25.3`) — for any box in a file that parses as an acceptance suite. The client sends the address; the server resolves it with `acceptance.locate()`, which **fails to resolve rather than resolving to something else**.

## The asymmetry this rests on

`Item.number` survives an edit elsewhere in the file, and when its own section changes it stops resolving. A position does the opposite: it always resolves, and after an edit it resolves to the wrong thing. That difference is the entire fix.

## Not a rewrite of check-toggle

Every other note in the corpus still uses the index path, and it is correct there — a note whose boxes all render has DOM order equal to source order. The address is **additive**: present on acceptance-suite boxes, absent elsewhere, and the endpoint prefers it when it is there.

## Done when

- [x] a rendered acceptance checkbox carries its check number as a data attribute
- [x] the write prefers the address and falls back to the index only where no address exists
- [x] an address that no longer resolves is **refused**, with the reason surfaced, and nothing is written
- [x] the reproduction in [[ISS-0184]] — DOM index 257 on `your-trainer`'s suite — writes to the row the user clicked, asserted against a throwaway copy
- [x] a note with no divergence keeps working through the index path, unchanged
- [x] mutations that must fail: prefer the index when an address exists; resolve a stale address to the nearest row; drop the name comparison

## Done 2026-08-17

`AcceptanceMarkTreeprocessor` stamps `data-check`, `data-check-name`, `data-mark` and `data-gating` on every acceptance row's `<li>`, and the client sends the **address**. `acceptance.locate()` resolves it and refuses when it no longer does.

**Registered at priority 26, above `task-list` (25), and that is the whole trick.** Below it, tasklist has already swapped `[ ]`/`[x]` for a stashed raw-HTML input, so neither the literal nor an element is in the tree and only the two marks it does *not* understand survive to be read — the exact inverse of what is wanted, which a first pass at priority 4 produced and which the tests now pin.

**The matcher uses `parse`'s own `_NAME_RE`.** A hand-rolled split on the first colon looked equivalent and truncated any name containing one — *"Imported intervals get translated (Layer 1: shared assignment)"* — leaving **70 of 579** rows unaddressed. With one regex for one convention it is 573 of 579.

The reproduction that opened [[ISS-0184]] was withdrawn the same day; this fix is justified by fragility rather than a live defect, and is needed regardless because the cycle has to carry a reason to a specific check.
