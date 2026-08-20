---
type: "[[issue]]"
id: ISS-0244
aliases: ["ISS-0244"]
title: "The release page draws a static check mark on every blocking row — a control that was disarmed rather than removed, identical on every row of the list where it appears"
status: open
owner: user:edwin
created: 2026-08-20
updated: "2026-08-20"
source: ["user:edwin"]
severity: low
component: cockpit-desktop
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[ISS-0210-The-Release-Page-Offers-Sixty-Live-Marks]]", "[[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]]", "[[ISS-0190-The-Acceptance-Tests-Sit-Last-On-Both-Release-Surfaces]]", "[[ISS-0224-The-Positional-Address-Outlived-The-Document]]"]
tests: []
---

# The mark stayed after the reason for it left

## Problem

Edwin, 2026-08-20, on the generated `your-trainer` release page: *"it shows the outstanding tests but it shows them with the check marks, just show them as a list of tst links like the features below."*

`gateGroup` puts `gateMark(item)` first on every row. That was correct when the mark was **the control** ([[ISS-0190]] put it in the row's left-hand column deliberately). [[ADR-0035]] then removed the click — [[ISS-0210]] found sixty live marks on the page whose entire purpose is to report that a release is *not* ready — and the glyph stayed behind as `is-static`.

**What is left is a decoration that is uniform where it appears.** The `Blocking` / `New` / `Chronic` / `Regressed` lists are, by construction, rows that are not settled — so every row shows the same glyph. It occupies the left-hand column and separates nothing from anything.

Two rows on the same page, for comparison:

```
feature   FEAT-0051   AI Workout Builder
gate      ☐  TST-0044  Paid, Key Configured — Generation …   AI Workout Builder
```

The feature row is what Edwin is pointing at: a typed id, a title, a click through to the note.

## The change is smaller than it looks

`item.number` **already resolves to `TST-0044`** on `your-trainer`. `Item.number` returns the positional address where one exists and the note id where it does not ([[ISS-0219]]), and those 89 checks carry no `number:` field at all — so the id is already on screen and already links to the check's own note.

So this is: drop `gateMark` on the unsettled lists, and give the id the features row's treatment (`scoped-row-id mono ov-typed`, `data-type="test"`).

## What must not be dropped with it

**`Quiet` and `Stale evidence` use the same `gateGroup`, and there the mark is not uniform.** A stale row is *ticked* — that is the whole of what makes it stale — so removing its glyph would erase the one thing distinguishing it from a blocking row. 53 of `your-trainer`'s ticked rows are in that group, and they are the reason its honest blocking number is 113 against a reported 60.

Proposal: drop the mark on `Blocking` / `New` / `Chronic` / `Regressed`; keep the distinction on `Quiet` and `Stale evidence`, in the row's meta text rather than as a glyph, so all six lists still read as one shape.

## Expected

```
TST-0044   Paid, Key Configured — Generation (Gemini)      AI Workout Builder
TST-0077   FREE at Cap Offers Nothing                      Monetization & Licensing
```

## Next Actions

- [ ] Drop `gateMark` on the four unsettled lists; align the id with the features row.
- [ ] Carry the ticked/stale distinction in meta text for `Quiet` and `Stale evidence`.
- [ ] A guard that fails if a gate list renders a glyph identical on every row — the general form, so this cannot come back as decoration a third time.
