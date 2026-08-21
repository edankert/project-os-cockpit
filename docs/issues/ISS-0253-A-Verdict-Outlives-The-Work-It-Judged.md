---
type: "[[issue]]"
id: ISS-0253
review_verdict: changes-requested
review_response: "2026-08-21: REVIEW-STALE walks the docs tree instead of note_index, which held no CHG-* note at all - 8 of the 51 terminal owed verdicts are change notes and every `merged` one is. The filed 49/43 did not reproduce; the measured figure at f5ca55b is 56 owed / 51 terminal (30 done, 8 merged, 4 implemented, 9 fixed) and the note now says so. || Second pass 2026-08-21: the measurement reproduces exactly (56 owed / 51 terminal; the note_index walk gives 43, missing precisely the 8 CHG-* notes). Finding F fixed - REVIEW_TERMINAL_STATUSES' comment still restated the refuted 27/7/4/5, a third copy of the same unmeasured number, and 'dating to 2026-08-02' was ISS-0253's date rather than the population's (measured: 2026-07-30, six notes)."
review_response_date: 2026-08-21
review_date: 2026-08-21
reviewed_by: model:claude-opus-5
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

> ⚠️ **The table below is the count filed on 2026-08-20 and it does not reproduce.** Corrected after independent review, 2026-08-21. Re-measured against `git archive f5ca55b` — the commit immediately before the fix — the figures are **56 owed verdicts, 51 of them terminal**:
>
> | status | filed | measured |
> |---|---|---|
> | `done` | 27 | **30** |
> | `merged` | 7 | **8** |
> | `implemented` | 4 | **4** |
> | `fixed` | 5 | **9** |
> | non-terminal | 6 | **5** |
> | **total / terminal** | 49 / 43 | **56 / 51** |
>
> **The finding is unaffected and the arithmetic was wrong**, which is the same shape this note is about: a number stated confidently and never re-counted. The validator now reports 51 and the first version of it reported 43 — *agreeing with the filed figure by coincidence*, because it read `note_index`, which holds no `CHG-*` note at all, and all 8 `merged` findings are change notes. **Two independent errors produced the same number.** See the fix below.

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

**`REVIEW-STALE`** in `tools/scripts/validate-docs.py` — a note at a terminal status carrying an owed verdict with no `review_response:` is reported. It fires on **51 notes** at `f5ca55b`.

> **It reported 43 for one commit, and that agreeing with the filed count was a coincidence of two errors.** The rule read `note_index`, and `build_note_index` holds **no `CHG-*` note at all**: `ID_PREFIXES` has no `CHG`, and a change note's id is `CHG-YYYYMMDD-Slug` rather than `CHG-0000`. Eight of the 51 are change notes and **every `merged` one is** — so the rule's own promotion comment described a population it was structurally incapable of producing, and `CHG-*` is one of the two types the review skill names as a *mandatory* trigger. It walks the files now. Found by independent review, 2026-08-21.

Warned with a promotion date (`2026-11-18`): clearing it is one honest line per note and that is a body of work, so [[project-os-dev#ADR-0011]] clause 3 forbids erroring over it. **None of the 51 was flipped**, which this issue's *"Not in scope"* names and which stands.

**The field shipped with nine adopters rather than none.** Independent review noted that a rule producing 51 warnings with no exemplar is a rule nobody can copy. [[ISS-0213]] carries the first — its three second-pass findings were applied in `4628aff` and nothing recorded it — and the eight notes this review round asked changes of carry the rest.

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

## Independent review — 2026-08-21

Fresh-context pass, separate session, `model:claude-opus-5`. Started from the notes and the diff `f5ca55b..07602db`; the author's reasoning trace was not available to it. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — same model as the author, recorded in `reviewed_by` as provenance. Every number below was re-measured and every guard re-executed against a constructed mutant rather than read.


**Verdict: changes-requested.** The mechanism is right and the rule works; the population it claims to describe is not the population it can see, and the filed numbers do not reproduce.

### The rule itself is sound

`review_response:` clearing the finding without touching the verdict is the correct shape, and it is guarded behaviourally. I deleted the `has_value((fm or {}).get("review_response"))` early-continue from `tools/scripts/validate-docs.py`: `test_recording_what_was_done_clears_it` and `test_it_does_not_re_arm_when_the_note_is_edited` both failed. The rejection of an `updated:`-based trigger is argued from measurement rather than taste, and `test_flipping_the_verdict_is_not_how_it_clears` pins the ADR-0011 property.

### Finding 1 (high) — `REVIEW-STALE` structurally cannot fire on a `CHG-*` note

`ID_PREFIXES` (`tools/scripts/validate-docs.py:63`) is `("ADR", "CHK", "DES", "FEAT", "ISS", "PHASE", "REQ", "RISK", "REL", "SUR", "TASK", "TST", "WF")`. There is no `CHG`. `build_note_index` keys off `extract_ids` and `ID_RE`, so **no change note ever enters `note_index`** — I confirmed it directly: `[k for k in idx if k.startswith("CHG")]` is empty.

The 43 the rule reports are 19 `FEAT`, 9 `ISS`, 5 `PHASE`, 4 `REQ`, 6 `TASK`. **Zero change notes, and therefore zero `merged` notes**, because every `merged` note in this corpus is a `CHG`.

This matters beyond arithmetic: a `CHG-*` note is the type `../../tools/skills/independent-review/SKILL.md` names as a *mandatory* review trigger (*"A change carries a `CHG-*` note"*). The rule is blind to the category most likely to carry a verdict.

### Finding 2 (high) — the filed numbers do not reproduce, and the "exactly 43" agreement is a coincidence

This note records *"49 notes carry `review_verdict: changes-requested` … of which 27 are done, 7 merged, 4 implemented and 5 fixed"*. Measured against `git archive f5ca55b` — the exact commit this was filed at:

| | filed here | measured at `f5ca55b` |
|---|---|---|
| total owed verdicts | 49 | **56** |
| at a terminal status | 43 | **51** |
| `done` / `merged` / `implemented` / `fixed` | 27 / 7 / 4 / 5 | **30 / 8 / 4 / 9** |

51 terminal − 8 `CHG` = **43**, which is what the rule emits. So [[CHG-20260821-Three-Silences-Get-A-Voice]]'s *"it fires on exactly 43 notes, which is the number ISS-0253 measured by hand"* is an undercount agreeing with a structurally-blind rule at the same integer. Nothing was confirmed by it.

The promotion comment in `validate-docs.py` inherits the error: it describes the population as *"27 `done`, 7 `merged`, 4 `implemented` and 5 `fixed`"* — a population the rule **cannot** produce, since it can report no `merged` note at all.

### Finding 3 (low) — the field ships with no exemplar

`grep -rl "^review_response:" docs/` returns **zero** notes. 43 warnings now stand and nothing demonstrates the shape that clears one — including [[ISS-0213]], whose second-pass findings were applied in `4628aff`, hours before this rule landed. Recording a response is not flipping a verdict, so it is not excluded by this note's own "not in scope" clause.

### What to change

1. Add `CHG` to `ID_PREFIXES`, or index change notes by path for this rule — then re-measure and correct **51** (or whatever it then reports) in this note, in the promotion comment, and in the `CHG` note.
2. Correct the filed breakdown above, or state the basis under which 49/43 was true.
3. Add a test constructing a terminal `CHG-*` note with an owed verdict. `tests/test_review_stale.py` has no such case, which is why the blind spot survived.

## Independent review — second pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `07602db..b635c39` — the first pass's findings and the author's reasoning trace were not available to it, only the seven claims as the notes state them. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]): same model as the author and as the first reviewer, recorded in `reviewed_by` as provenance. Every number below was re-measured and every guard re-executed against a constructed mutant.

**Finding F (low-medium) — the corrected sentence kept one refuted number, and the refuted breakdown survives in three more places.** The `PROMOTIONS` comment now reads *"**51 findings** … 30 `done`, 8 `merged`, 4 `implemented`, 9 `fixed`, **dating to 2026-08-02**"*. The earliest `review_date` among those 51 is **2026-07-30**, on six notes: `CHG-20260730-Two-Features-Closed`, `FEAT-0045`, `ISS-0037`, `ISS-0057`, `ISS-0068`, `ISS-0069`. Three of the four figures in that sentence were re-measured; the date was carried over from this note's filing. And the numbers this note's own correction calls *"a coincidence of two different errors"* are still asserted in the present tense at `tools/scripts/validate-docs.py:279` (*"the population it describes is 27 `done`, 7 `merged`, 4 `implemented` and 5 `fixed`"*), in the rule's header comment (*"49 notes carry `changes-requested`, 43 of them at a terminal status"*) and twenty lines further down (*"Six of the 49 are that"*). One file now states both populations.

**Note on the rule's live effect.** At `b635c39` the rule still fires on the same 51 notes; the nine `review_response:` adopters are additional owed verdicts stamped by the first pass, not clearances of the 51. `REVIEW-STALE` is a warning until `2026-11-18`, which is why `validate-docs.sh` reports OK.
