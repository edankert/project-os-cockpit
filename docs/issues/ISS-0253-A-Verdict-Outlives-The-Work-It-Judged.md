---
type: "[[issue]]"
id: ISS-0253
aliases: ["ISS-0253"]
title: "`review_verdict` is sticky and nothing refreshes it, so 43 notes are closed while still reading `changes-requested` — the record says work was rejected that was fixed weeks ago"
status: open
owner: user:edwin
created: 2026-08-20
updated: "2026-08-20"
source: ["measured while closing PHASE-037, 2026-08-20"]
severity: medium
component: docs
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[ISS-0121-Ten-Owed-Rows-Were-False]]", "[[ADR-0011-Independent-Review]]", "[[ADR-0013-Independence-Is-Clean-Context]]", "[[ISS-0229-Steps-Proven-Is-Sent-And-Nothing-Draws-It]]"]
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

Because the author flipping their own verdict is exactly what [[ADR-0011]] exists to prevent. A verdict is the reviewer's, and self-clearing it turns an independent gate into a formality — which is why every one of these 43 was left alone deliberately, and correctly.

**The gap is that "the findings were addressed" has nowhere to go.** The only mechanism that can clear a verdict is another review pass, and there is no signal that one is owed. Nothing counts these; nothing surfaces them; a person reading a closed feature cannot tell a live objection from a settled one.

## What it costs

It made this exact list unreadable during PHASE-037's close-out: *"five verdicts remain at changes-requested"* was reported repeatedly as outstanding work, when what was outstanding was **a re-review, not a fix**. Measured properly it is not five but forty-nine, and the number is meaningless without knowing which still describe live objections.

## Options

1. **A `review_response:` field** — the author records *what was done about each finding*, dated, without touching the verdict. Cheap, honest, and preserves the gate: the reviewer's judgement stands, and the response sits beside it.
2. **Stale-verdict detection in the validator** — a note at a terminal status carrying `changes-requested` with `updated:` later than `review_date:` is *reported*, so re-review is a visible obligation rather than a thing nobody counted. Pairs naturally with option 1.
3. **Require a fresh pass before terminal status** — strongest, and probably too strong: it would have blocked most of today's closures over verdicts whose findings were demonstrably fixed in the same commit.

Recommendation: **1 and 2 together.** The verdict stays the reviewer's; the response becomes recordable; and the validator makes an unrefreshed verdict visible instead of silently permanent.

## Not in scope

Flipping any of the 43. Every one of them is the reviewer's to change, and this issue exists precisely because the author doing it would be the wrong fix.
