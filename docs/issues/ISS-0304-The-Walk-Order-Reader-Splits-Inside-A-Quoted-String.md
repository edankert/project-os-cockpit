---
type: "[[issue]]"
id: ISS-0304
aliases: ["ISS-0304"]
title: "A comma inside a quoted walk-order entry splits it into two, so one item on the bench becomes two half-sentences"
status: fixed
severity: low
phase: "[[PHASE-043-The-Walk-Page]]"
owner: user:edwin
created: 2026-09-13
updated: 2026-09-13
source: ["Writing this repo's docs/tests/acceptance/WALK.md, 2026-09-13"]
area: "the walk"
component: "tools/scripts/walk-sheet.py"
severity_note: ""
affects: ["[[FEAT-0149-The-Walk-Page]]"]
related: ["[[TASK-0618-The-Walk-Payload]]"]
tags: [issue, acceptance, upstream]
---

# A comma inside a quoted walk-order entry splits it

## What happens

Written in `docs/tests/acceptance/WALK.md`:

```yaml
bench: ["A second device on the same Wi-Fi, for the tablet row"]
```

The sheet and the page both print two bench items:

```
- A second device on the same Wi-Fi
- for the tablet row
```

## Why it matters

`bench:` is prose a person reads while setting up — *"a second trainer for the mid-ride swap row"*, *"a heart-rate strap, charged"*. A comma in a sentence of that kind is ordinary, and the second half becomes a bench item that is not a thing: **"for the tablet row"** is an instruction to fetch nothing.

It is quiet. Nothing warns, and a walker reading the sheet has no way to tell a split entry from two entries somebody wrote.

## Where it is

Upstream, `tools/scripts/walk-sheet.py`, `_inline_list`:

```python
return [p.strip().strip("\"'") for p in raw.split(",") if p.strip()]
```

It splits first and strips quotes after, so the quotes never protect anything. `surfaces:` and `checks:` carry ids and area names, which rarely hold a comma; `bench:` is the field written as sentences, which is where it shows.

## What a fix looks like

Split respecting quotes — the walk order's own `_strip_comment` already walks a string character by character tracking a quote, so the shape is there to follow. **Not a fix to make here**: the bundled copy is asserted byte-identical to upstream's, and a local patch is how one rule becomes two.

Until then, this repo's `WALK.md` says so and writes bench entries without commas.

## Owner

project-os-dev, FEAT-0029.

## Homed under PHASE-043, after a detour through the parking lot

It was parked under [[PHASE-999-Future]] for part of a day, on the argument that a phase should not stay open for a repair that belongs in another repository. That argument stopped applying the moment the repair landed: a note at `fixed` sitting in the parking lot is what `test_no_terminal_note_sits_in_the_parking_lot` exists to catch, and it caught this. The issue was found by PHASE-043, fixed the same day, and belongs to it.

## Fixed upstream, 2026-09-13

`_inline_list` now walks the string character by character tracking a quote, following `_strip_comment`'s shape as this note suggested. `bench: ["A second device on the same Wi-Fi, for the tablet row", "The tablet"]` yields two items, not three, and `tools/scripts/test-walk-sheet.sh` asserts both that the sentence survives intact and that no half-sentence reaches the bench list. Reverting to the naive split fails two assertions.

This repo's `WALK.md` can now write bench entries with commas in them.

`src/project_os_cockpit/walk_sheet_bundled.py` has been re-copied and `tests/test_walk_bundle.py` passes.
