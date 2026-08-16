---
type: "[[feature]]"
id: FEAT-0111
aliases: ["FEAT-0111"]
title: "The marks and verdicts the record already uses become writable — a check can be left open with a reason and a passed check can carry its witness"
status: done
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["Edwin 2026-08-16: 'The acceptance tests do not support the new intentionally left open option and do not support adding text'", "[[ISS-0181-Four-Things-The-Release-Surface-Cannot-Do]]", "Independent functionality review of PHASE-034, 2026-08-16 — the convention already exists in ../your-trainer's own suites"]
goal: "Close ISS-0181's first two items with the vocabulary already in the record rather than a new one. The mark and the text slot exist, are used consistently across two of your-trainer's suites, and were invented a second time in this repo in a form nothing else writes."
requirements: []
tasks: ["[[TASK-0454-Read-And-Write-The-Marks-Already-In-Use]]", "[[TASK-0455-A-Check-Carries-Its-Verdict-And-Its-Witness]]"]
design: ""
release: ""
depends: []
related: ["[[ISS-0181-Four-Things-The-Release-Surface-Cannot-Do]]", "[[ISS-0177-An-Exception-Mark-Drops-A-Check-With-No-Justification]]", "[[ISS-0141]]", "[[FEAT-0104-The-Suite-Is-The-Surface]]", "[[FEAT-0107-Publication-Is-A-List-Of-Releases]]", "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"]
tests: ["[[TST-0037-FEAT0111]]"]
---

# The marks the record already uses

## I invented a mark that already existed

[[ISS-0181]] items 1 and 2 read as a design problem — *there is no way to mark a check intentionally left open, and no way to attach text to one.* They are not. Both exist, in `../your-trainer`'s own suites, used consistently and with a grammar.

`ACCEPTANCE_TESTS_v2.1.0.md` carries **6 `[~]` and 1 `[F]`**, each with a dated verdict and a reason:

> `- [F] **Per-rider collapse persistence:** … **FAILS 2026-06-07** — collapse state is stored globally in SharedPreferences, not per-rider. Tracked as [[ISS-0285-SectionCollapseStateNotPerRider]] (medium severity) — defer to v2.1.1.`

> `- [~] **AI Workout Builder generate-mode — MCP path (Pro, non-English locale):** … **Partial pass 2026-06-06**: English-looking prompts come back in English even when the app locale is German (see [[ISS-0277]] — low severity, may not fix).`

The grammar is stable: **`**<VERDICT> <DATE>** — <reason> [[ISS-link]]`**, appended to the check's own text. Verdicts observed in use: `Verified`, `Partial pass`, `Open`, `Not reproduced`, `FAILS`, `Blocked`.

And `ACCEPTANCE_CHECKLIST_v2.1.1.md` adds the other half — **the witness, 22 times**:

> `- [x] **[BOTH]** **ISS-0343 HRM reconnects across a rotating address** … ✅ (Claude, tablet: address rotated 7F:D5:FB:49:A4:DF → 73:DD:28:D6:8D:50; reconnected by name-match, slot shows Connected)`

> `- [x] **[TABLET]** **HR tile is live** … ✅ (Claude saw 69 bpm this session)`

Plus `{ED: unable to test since there is no online library route extension}` for the human's own escapes.

**So there is nothing to design.** This repo introduced `[!]` for the same purpose, in a form no suite in the fleet writes, and left it parse-only — [[ISS-0177]] records that a hand-written `[!]` drops a check from the gate today with no justification and nothing owed. The correction is to adopt what is in use and let `[!]` remain readable rather than promoted.

## What the buttons write

| action | writes | effect on the gate |
|---|---|---|
| pass | `- [x] … ✅ (<witness>, <date>: <what was observed>)` | satisfied |
| partial | `- [~] … **Partial pass <date>** — <reason> [[ISS-…]]` | reconciled — not blocking, [[ISS-0141]] |
| fail | `- [F] … **FAILS <date>** — <reason> [[ISS-…]]` | **blocking**, and it should stay that way |
| leave open | unchanged | blocking |

`[F]` is the interesting case: the parser reads an unrecognised mark as blocking, which for a *failed and tracked* check is exactly right and should not be "fixed" into a pass. It is recorded here so that nobody later reads it as a parser gap and closes it.

`rewrite_check()` already takes a `note` parameter and appends it to the line. **The write path exists.** Only the vocabulary was invented in the wrong place.

## Acceptance criteria

- [x] `[~]` and `[F]` are read, written, and rendered with distinct meanings, and `[!]` remains readable without being offered.
- [x] A partial or a failure **requires** a reason before it can be written — the mark and the text are one action, not two.
- [x] A pass may carry a witness and does not require one.
- [x] The text is appended in the **grammar already in the record**, verbatim in shape: `**<Verdict> <date>** — <reason>` for partial/fail, `✅ (<witness>)` for a pass.
- [x] An `ISS-*` referenced in a reason is written as a **wikilink** and resolves.
- [x] Round-trip: a row written by the tool parses back to the mark and the text it was given, and a row written **by hand** in the existing grammar parses identically.
- [x] The `mtime` guard and name comparison from [[FEAT-0103]] still refuse a write to a suite that moved underneath the edit.
- [x] `../your-trainer`'s existing 6 `[~]` and 1 `[F]` parse to the same verdicts after this lands as before it — no existing row changes meaning.

## How this is verified

A `TST-*` that round-trips each mark through parse → write → parse, plus a corpus assertion that the seven rows already carrying these marks in `../your-trainer` are unchanged. Mutations to defeat: write the mark without the text; accept an empty reason on a fail; write `[!]` where `[~]` was chosen; drop the date.

## Scope — what of ISS-0181 this closes

**Closes items 1 and 2.** Items 3 and 4 stay open on [[ISS-0181]] and are not addressed here:

- **Item 3, the save/reload interruption**, is an editing-interaction problem — tick, write, watcher, re-render — and is about the file-watch path rather than the vocabulary. It needs its own treatment.
- **Item 4, completing a release**, needs [[FEAT-0108]] and [[FEAT-0109]] underneath it. [[FEAT-0110]] supplies the *after*; the ship transition itself is deliberately not planned yet.

Saying so here rather than letting the issue quietly look resolved: this phase has already closed a feature at zero ticked criteria twice, and an issue half-fixed by a feature that claims it is the same shape.
