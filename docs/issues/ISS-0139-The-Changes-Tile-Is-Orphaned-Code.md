---
type: "[[issue]]"
id: ISS-0139
aliases: ["ISS-0139"]
title: "fillChanges and /api/cockpit/changes survive with no caller and no consumer — the tile FEAT-0052 replaced left its code behind"
status: "fixed"
severity: low
owner: user:edwin
created: 2026-08-11
updated: "2026-08-13"
phase: ""
features: ["[[FEAT-0052]]"]
tasks: []
related: ["[[FEAT-0048-Changes-On-The-Overview]]", "[[REL-0001-The-Human-Has-Levers]]"]
tags: [issue, dead-code]
---

# The Changes tile is orphaned code

## What was found

Walking [[REL-0001]]'s check *"changes read on the overview: recent change notes in the history band, older ones collapsed by month and still openable"* on 2026-08-11: **the overview has no Changes band.** Its only sections are `Phases` and `History`.

That is correct behaviour, not a regression — see the reconcile note on the check itself. [[FEAT-0052]] (`2eec1a4`, 2026-07-30) deliberately replaced three tiles with one: *"the overview had three history tiles answering one question three ways."* The commit removed `buildChangesTile()` from the overview's assembly.

**What it did not remove is the code behind it:**

- `renderer.ts :: fillChanges` — ~50 lines, `interface ChangesPayload`, and a `fetch` — **defined and never called.** `grep -n fillChanges` returns exactly one line, its own definition.
- `GET /api/cockpit/changes` — still served, still computing 126 change notes into `recent` + month buckets with per-week subgroups. **Nothing consumes it.**

## Why it is worth a note rather than nothing

It cost this pass real time: the payload was fetched, the buckets looked right (`Last week · 12`, `Earlier this month · 4`, `July 2026`, `May 2026`), and the month buckets reported `items: 0` — which reads like a bug until you notice they nest their weeks in `subgroups`. All of that investigation was of a surface that no longer exists.

Dead code that still answers correctly is the expensive kind: it survives every test, reads as live to the next person, and misdirects exactly the reader who is being careful.

## Resolution

Either delete both, or — if the archive is wanted back — say where. The check it served is being reconciled as **cut** rather than left open, so nothing depends on this decision.

## Correction — 2026-08-11: half of this is wrong, and it is the half that says "delete both"

**`GET /api/cockpit/changes` has a live consumer.** `buildQuickCorpus` fetches it at `renderer.ts:10044` — deliberately, under the comment *"Changes and tests have no nav mode … Both are still worth finding by name"* — and that is how change notes reach the quick-switch palette. Observed the same day in the live harness: typing `CHG-20260811` returns two rows, which can only have come from that endpoint.

So the two halves of this issue have different answers:

- **`fillChanges` is dead** — `grep` still returns one line, its own definition. That was and is correct.
- **The endpoint is load-bearing.** Deleting it would silently remove 126 change notes from the only surface that can find them by name.

The original text found the endpoint by reading the overview's assembly and concluded from its absence there; the consumer is 2,700 lines away in a function about something else. *Dead code and code you have not found yet look identical from the call site you happened to read* — which is the same lesson this issue was filed to teach, taken one level further in.

Related: [[ISS-0142]], which is what came of reading `buildQuickCorpus` closely enough to find this — releases are the one type that never got the patch changes and tests both have.

## Fixed — 2026-08-13

*(`phase:` cleared from `[[PHASE-999-Future]]` at the same time. The sentinel answers "which phase will deliver this", and once the work has shipped that question is a category error — [[PHASE-015]]'s rule, and `test_no_terminal_note_sits_in_the_parking_lot` caught it the moment this note went terminal. Nothing delivered it but a bug batch with no phase, which is what an empty value says.)*

`fillChanges` and its Changes-tile comment block are gone — 57 lines that nothing called.

**The endpoint stays, and so does `ChangesPayload`**, exactly as this issue's own correction insisted: `buildQuickCorpus` fetches `/api/cockpit/changes` so change notes can be found by name, and the type is that consumer's now. The comment left in place says so, because the next person to grep for the tile will find the same absence that produced this issue's first, half-wrong draft.
