---
type: "[[change]]"
id: CHG-20260817
title: "The acceptance tests lead both release surfaces, the delta rows wear the document's own mark control, and the suite opens from a file row"
status: merged
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["Edwin 2026-08-17, from use: 'move the acceptance tests section to the top of the next release section (left pane) since this needs to be completed (the features/issues are things that simply ship with this release), also move it to the top in the overview section'", "Edwin 2026-08-17: 'remove the open the acceptance tests button, just show this as a file link instead'"]
related: ["[[ISS-0190-The-Acceptance-Tests-Sit-Last-On-Both-Release-Surfaces]]", "[[FEAT-0108-The-Gate-Is-A-Delta-Not-A-Census]]", "[[FEAT-0111-The-Marks-The-Record-Already-Uses]]"]
tags: [publication, surfaces, acceptance]
---

# The errand comes first

## What changed

**The acceptance tests lead a release, on both surfaces.** In the navigator, `Acceptance tests` is the first subgroup of a release group, ahead of `Features`, `Issues` and `Documents`. On the release page, the release gate is the first section, above *What's in it*.

The ordering follows from what the reader has to do rather than from how the record is structured. Everything else a release group carries is **inventory** — the features and issues it ships. The suite is the only part of it that is an **errand**.

**Gate rows wear the document's own mark control.** `Pass · Partial · Fail` on the right of each row is gone; the mark the file holds is drawn on the left, and clicking it opens the same six-mark dialog, with the same shared reason field, writing through the same `POST /api/notes/mark-check`. The two surfaces showing one check now speak one vocabulary.

Rows that are not a thing to walk — the collapsed `Quiet` and `Stale evidence` groups — show their mark and do not offer it. They never carried a verdict button either.

**The suite opens from a file row.** `Open the acceptance tests` was a primary button; every other file on the release page is a row you click, and now so is this one.

**The delta groups read as lists rather than as prose.** Heading, count and hint sit on one line with the count as a chip; an empty group says what empty *means* for it rather than `None.`

## What a person will notice

| | before | after |
| --- | --- | --- |
| a release in the navigator | Features · 78, Issues, Acceptance tests · 1, Documents | Acceptance tests · 1, Features · 78, Issues, Documents |
| the release page | five sections of inventory, then the gate | the gate, then the inventory |
| marking a check from the gate | three buttons, three verbs, on the right | one mark on the left, six choices, the document's dialog |
| a check that failed | `[ ]` and the word `failed` in the meta | `[!]`, in the file's own notation, at the left edge |
| opening the suite | a primary button mid-section | `suite docs/tests/ACCEPTANCE_TESTS.md` |
| an empty `Regressed` | `None.` | `No check ticked at v2.1.6 has come unticked. Zero here also means nobody touched the suite, which is not the same as nothing breaking.` |

## Payload

`acceptance.Item` carries `mark` — the character the file writes — and every gate row emits it. The five booleans derived from it are lossy by design (`x`/`X` are one thing to the gate, `/`/`~` likewise), so a surface that *draws* the mark could not have reconstructed it.

Additive: a client reading an older payload gets `[ ]`, which is what an unsettled row almost always is.

## Not changed

The write path, its refusals, and the grammar it writes. A partial, a canceled, a failed or a question is still refused without a reason, and a reason still cannot cite a note that does not exist.
