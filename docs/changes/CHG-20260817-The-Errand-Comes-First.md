---
type: "[[change]]"
id: CHG-20260817
title: "The acceptance tests lead both release surfaces, the delta rows wear the document's own mark control, and the navigator reports the gate rather than asserting `ready`"
status: merged
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["Edwin 2026-08-17, from use: 'move the acceptance tests section to the top of the next release section (left pane) since this needs to be completed (the features/issues are things that simply ship with this release), also move it to the top in the overview section'", "Edwin 2026-08-17: 'remove the open the acceptance tests button, just show this as a file link instead'", "Edwin 2026-08-17: 'Don't call the acceptance tests suite also, at the moment it is unclear what the acceptance tests status is from the left-pane, it says ready at the moment which is very unlikely?'"]
related: ["[[ISS-0190-The-Acceptance-Tests-Sit-Last-On-Both-Release-Surfaces]]", "[[ISS-0191-The-Left-Pane-Calls-The-Acceptance-Tests-A-Suite-And-Says-They-Are-Ready]]", "[[FEAT-0108-The-Gate-Is-A-Delta-Not-A-Census]]", "[[FEAT-0111-The-Marks-The-Record-Already-Uses]]"]
tags: [publication, surfaces, acceptance]
---

# The errand comes first

## What changed

**The acceptance tests lead a release, on both surfaces.** In the navigator, `Acceptance tests` is the first subgroup of a release group, ahead of `Features`, `Issues` and `Documents`. On the release page, the release gate is the first section, above *What's in it*.

The ordering follows from what the reader has to do rather than from how the record is structured. Everything else a release group carries is **inventory** — the features and issues it ships. The acceptance tests are the only part of it that is an **errand**.

**Gate rows wear the document's own mark control.** `Pass · Partial · Fail` on the right of each row is gone; the mark the file holds is drawn on the left, and clicking it opens the same six-mark dialog, with the same shared reason field, writing through the same `POST /api/notes/mark-check`. The two surfaces showing one check now speak one vocabulary.

Rows that are not a thing to walk — the collapsed `Quiet` and `Stale evidence` groups — show their mark and do not offer it. They never carried a verdict button either.

**The acceptance tests open from a file row.** `Open the acceptance tests` was a primary button; every other file on the release page is a row you click, and now so is this one.

**The delta groups read as lists rather than as prose.** Heading, count and hint sit on one line with the count as a chip; an empty group says what empty *means* for it rather than `None.`

## What a person will notice

| | before | after |
| --- | --- | --- |
| a release in the navigator | Features · 78, Issues, Acceptance tests · 1, Documents | Acceptance tests · 60 unchecked, Features · 78, Issues, Documents |
| the release page | five sections of inventory, then the gate | the gate, then the inventory |
| marking a check from the gate | three buttons, three verbs, on the right | one mark on the left, six choices, the document's dialog |
| a check that failed | `[ ]` and the word `failed` in the meta | `[!]`, in the file's own notation, at the left edge |
| opening the acceptance tests | a primary button mid-section | `tests docs/tests/ACCEPTANCE_TESTS.md` |
| an empty `Regressed` | `None.` | `No check ticked at v2.1.6 has come unticked. Zero here also means nobody touched the acceptance tests, which is not the same as nothing breaking.` |

## Payload

`acceptance.Item` carries `mark` — the character the file writes — and every gate row emits it. The five booleans derived from it are lossy by design (`x`/`X` are one thing to the gate, `/`/`~` likewise), so a surface that *draws* the mark could not have reconstructed it.

Additive: a client reading an older payload gets `[ ]`, which is what an unsettled row almost always is.

## Second round, same day ([[ISS-0191-The-Left-Pane-Calls-The-Acceptance-Tests-A-Suite-And-Says-They-Are-Ready]])

Moving the acceptance tests to the top of the navigator made it obvious that the row there **had no state**. Edwin, on seeing it: *"it is unclear what the acceptance tests status is from the left-pane, it says ready at the moment which is very unlikely?"*

**The row reads the gate.** `status` was the literal `"ready"` — which in this vocabulary means *defined and never executed* — hard-coded, so it claimed that nothing in a 505-check suite had ever been walked, and would have gone on claiming it whatever was marked. It is `blocked` while any Tier 1/Tier 2 check is unsettled and `passing` when none is, computed by `acceptance.gate_payload`, the same call behind the release page's `Release gate · N unchecked`.

**The group label carries the number.** `Acceptance tests · 60 unchecked`, not `Acceptance tests · 1` — the old count was of files, under a label that reads as a count of tests.

**Nothing user-facing says `suite`.** It was the label on the file row and one line of prose. The internal identifiers — `SUITE_REL`, `class Suite` — name a Python object and stay.

**A repo with no acceptance tests gets no dead row.** The navigator row was appended unconditionally against a hard-coded path. It is emitted only when the file exists now, and the release page states the absence rather than rendering nothing, because an empty gate must never read as a clear one.

| | before | after |
| --- | --- | --- |
| the navigator row | `ready`, always | `blocked · 60 of 505 Tier 1/2 checks unwalked`, or `passing · all 505 settled` |
| the group label | `Acceptance tests · 1` | `Acceptance tests · 60 unchecked` |
| the file row on the page | `suite  docs/tests/…` | `tests  docs/tests/…` |
| a repo with no suite | a navigator row to a 404, and a page that said nothing | no row, and `Release gate · cannot be evaluated` |

## Not changed

The write path, its refusals, and the grammar it writes. A partial, a canceled, a failed or a question is still refused without a reason, and a reason still cannot cite a note that does not exist.
