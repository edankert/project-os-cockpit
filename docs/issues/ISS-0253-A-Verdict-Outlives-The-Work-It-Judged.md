---
type: "[[issue]]"
id: ISS-0253
aliases: ["ISS-0253"]
title: "`review_verdict` is sticky and nothing refreshes it, so 43 notes are closed while still reading `changes-requested` — the record says work was rejected that was fixed weeks ago"
status: fixed
owner: user:edwin
created: 2026-08-20
updated: "2026-08-21"
source: ["measured while closing PHASE-037, 2026-08-20"]
severity: medium
component: docs
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[ISS-0121-Ten-Owed-Rows-Were-False]]", "[[project-os-dev#ADR-0011]]", "[[project-os-dev#ADR-0013]]", "[[ISS-0229-Steps-Proven-Is-Sent-And-Nothing-Draws-It]]"]
tests: []
---

# A verdict outlives the work it judged

## Measured

**49 notes carry `review_verdict: changes-requested`.** Of those, **43 are at a terminal status**:

| status | notes |
|---|---|
| `done` | 27 |
| `merged` | 7 |
| `implemented` | 4 |
| `fixed` | 5 |
| non-terminal (`planned`, `open`, `active`) | 6 |

They date back to **2026-08-02**. Twenty-two are from today alone.

## The problem

A verdict is a **fact about a moment**: *"reviewed on this date, against this state, and changes were requested."* Every one of those 43 is true in that sense and false as a description of the note today — the findings were acted on, often within the hour, and nothing writes a new verdict.

So the field is **sticky in the unhelpful direction**: a note whose findings were all fixed reads, forever, as work a reviewer rejected.

This is [[ISS-0121]] inverted. That issue found `review_verdict` sticky in the *other* direction — a row reviewed once read as reviewed forever, and all ten owed rows were false. The renderer stopped reading the field alone because of it. **The same stickiness is here, unaddressed, on the authoring side.**

## Why it is not simply "the author should flip it"

Because the author flipping their own verdict is exactly what [[project-os-dev#ADR-0011]] exists to prevent. A verdict is the reviewer's, and self-clearing it turns an independent gate into a formality — which is why every one of these 43 was left alone deliberately, and correctly.

**The gap is that "the findings were addressed" has nowhere to go.** The only mechanism that can clear a verdict is another review pass, and there is no signal that one is owed. Nothing counts these; nothing surfaces them; a person reading a closed feature cannot tell a live objection from a settled one.

## What it costs

It made this exact list unreadable during PHASE-037's close-out: *"five verdicts remain at changes-requested"* was reported repeatedly as outstanding work, when what was outstanding was **a re-review, not a fix**. Measured properly it is not five but forty-nine, and the number is meaningless without knowing which still describe live objections.

## Options

1. **A `review_response:` field** — the author records *what was done about each finding*, dated, without touching the verdict. Cheap, honest, and preserves the gate: the reviewer's judgement stands, and the response sits beside it.
2. **Stale-verdict detection in the validator** — a note at a terminal status carrying `changes-requested` with `updated:` later than `review_date:` is *reported*, so re-review is a visible obligation rather than a thing nobody counted. Pairs naturally with option 1.
3. **Require a fresh pass before terminal status** — strongest, and probably too strong: it would have blocked most of today's closures over verdicts whose findings were demonstrably fixed in the same commit.

Recommendation: **1 and 2 together.** The verdict stays the reviewer's; the response becomes recordable; and the validator makes an unrefreshed verdict visible instead of silently permanent.

**Both built 2026-08-21.** See below.

## Not in scope

Flipping any of the 43. Every one of them is the reviewer's to change, and this issue exists precisely because the author doing it would be the wrong fix.


## Fixed 2026-08-21 — options 1 and 2, together

**`review_response:` (and `review_response_date:`)** — a second field, beside the verdict, where *"the findings were addressed"* goes. It **does not touch `review_verdict`**, and `test_recording_what_was_done_clears_it` asserts the verdict is still `changes-requested` in the file afterwards. A verdict is the reviewer's; self-clearing it turns an independent gate into a formality, which is the whole reason this issue exists.

**`REVIEW-STALE`** in `tools/scripts/validate-docs.py` — a note at a terminal status carrying an owed verdict with no `review_response:` is reported. It fires on **exactly 43 notes** on the day it landed, which is the number this issue measured by hand, arrived at independently by the rule.

Warned with a promotion date (`2026-11-18`): clearing it is one honest line per note and that is a body of work, so [[project-os-dev#ADR-0011]] clause 3 forbids erroring over it. **None of the 43 was flipped**, which this issue's *"Not in scope"* names and which stands.

### The trigger that was deliberately not used

*"`updated:` later than `review_date:`"* is the obvious rule and it is wrong twice over:

- [[ISS-0007]] records that an `updated:`-date heuristic **re-arms a gate whenever a note is edited for any reason** — that is the exact mechanism that issue removed.
- Stamping a verdict **is** an edit, so `cockpit._verdict_is_owed`'s own measurement holds here: 85 of 103 verdicts in this corpus have `updated <= review_date`, and the comparison would call them all still-owed, backwards.

So the discriminator is **whether an answer was recorded**, which is a fact rather than a proxy for one. `test_it_does_not_re_arm_when_the_note_is_edited` drives three `updated:` dates either side of the review and asserts silence for all three.

### Where a reader now sees it

The review desk's register row says `answered <date>` or `no response recorded` on every row whose verdict asked for something — which is the cost this issue named: *"a person reading a closed feature cannot tell a live objection from a settled one."*

**[[ISS-0121]]'s discriminator is untouched.** `owed` is still server-computed from the note's current status; this adds a second axis rather than replacing the first, and `test_the_desk_does_not_read_the_verdict_alone` pins that.

### Three copies of one vocabulary, pinned

`OWED_VERDICTS` now exists in `cockpit.py`, in the validator (stdlib-only, cannot import the cockpit) and in `renderer.ts` (TypeScript). `test_the_validator_and_the_cockpit_agree_on_which_verdicts_owe` reads all three and requires them equal.

### Four mutants, four catches

| mutant | caught by |
|---|---|
| the terminal-status filter is dropped | `test_a_note_still_in_flight_is_not_reported` |
| recording a response no longer clears it | `test_recording_what_was_done_clears_it` |
| an `approved` verdict is reported too | `test_an_approved_verdict_is_not_reported` |
| the desk stops saying whether it was answered | `test_the_desk_says_whether_the_objection_was_answered` |

### What this does not do

It does not make a re-review happen. It makes the obligation **countable and visible**, which is the difference between a gap somebody can act on and one nobody had a number for. The 43 are now a list, not a feeling.
