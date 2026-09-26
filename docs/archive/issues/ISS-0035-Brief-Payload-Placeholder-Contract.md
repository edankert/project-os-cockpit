---
type: "[[issue]]"
id: ISS-0035
aliases: ["ISS-0035"]
title: "brief_payload returns placeholder text in sections, and one placeholder anywhere denies a parsed identity"
status: fixed
severity: high
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["independent review 2026-07-28 (FEAT-0043)"]
related: ["[[TASK-0223-Brief-Payload-And-Identity-Band]]", "[[REQ-0024-Brief-Is-Maintained]]", "[[FEAT-0043-Design-Top-Level-Surface]]"]
fixed_by: []
---

# Two defects in one contract

## 1. The placeholder text is returned

`sections[].body` is unscrubbed. An unfilled brief yields `{"heading": "Project Identity", "body": "- Name: REPLACE ME\n- Purpose: REPLACE ME"}`.

The docstring says the placeholder is "deliberately **not** returned" and the test is named `test_placeholder_text_is_never_returned` — but it asserts only that `name` and `purpose` are blank. Rendering `brief.sections` in the unfilled branch would put `Purpose: REPLACE ME` on the surface with every test still green. The name of the test is a claim the test does not make.

## 2. One placeholder anywhere denies the whole identity

`state` is `unfilled` whenever `placeholders > 0` **anywhere in the file**. With Name and Purpose genuinely filled and a single `REPLACE ME` left under `## Invariants`, the payload parses the real values and then reports `unfilled`, so the band returns early and headlines "This project has not said what it is" — about a project that has.

TASK-0223 argued both "a half-filled brief keeps what is real" and "the unfilled branch returns before touching name/purpose". The second nullifies the first at the only consumer. The first is the correct instinct; the state field is the wrong shape for it.

## Fix direction

Scrub placeholder lines out of `sections[].body` so the payload's stated contract is its actual contract, and make `state` reflect whether the *identity* is filled rather than whether the file is finished — keeping the placeholder count so the surface can still say the rest needs work.

## Resolution (2026-07-28)

**Scrubbing is per line, in every field a surface could render.** `sections[].body` now drops lines matching the placeholder pattern, keeping the rest — a section that is nothing but placeholders disappears, which is right, because it says nothing. A real invariant sitting next to a `REPLACE ME` survives, because discarding a half-written section would punish progress. `test_the_band_never_renders_the_placeholder` was rewritten to assert the property it is named for: no field of the payload contains the text. Mutating the scrub away fails it.

**`state` describes the identity, not the file.** `filled` iff a real name *and* purpose survive. A brief with both plus a stray `REPLACE ME` under a later heading is now `filled` — it has said what it is — while `placeholders` still counts every one so the surface can say the rest needs work.

A third thing fell out that neither the review nor the original task had noticed: **the two are independent in both directions.** A brief can be incomplete with *zero* placeholders, when someone deleted the template lines instead of filling them. The band said "carries 0 template placeholder(s)" in that case; the copy is now built from what is actually true of the file.

**The unfilled band leads with what is known.** `Name — the brief is unfinished` when a name survived, rather than "This project has not said what it is" over a name the payload just parsed. The original rule (return before touching name/purpose) was defending the right property by the wrong means: `name` is already scrubbed, so it is always safe to render, and the leak was somewhere the rule did not look.
