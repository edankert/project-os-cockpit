---
type: "[[requirement]]"
id: REQ-0045
aliases: ["REQ-0045"]
title: "The mark is stored as a word and displayed as a check mark, and no surface may render the stored form"
status: implemented
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-20"
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: changes-requested
priority: medium
scope: "acceptance surfaces"
implements: "[[FEAT-0126-A-Rendered-Mark-Is-A-Check-Mark]]"
acceptance:
  - "[ ] Every surface that shows a mark renders it through one map; none reads `mark` directly."
  - "[ ] A guard fails if a raw mark word (`done`, `todo`, `canceled`, …) reaches a rendered surface."
  - "[ ] Storage is unchanged: the notes still carry words, per ISS-0200."
covers: []
related: ["[[ISS-0211-The-Mark-Picker-Shows-Words-Where-The-Check-Mark-Was]]", "[[ISS-0200-Marks-Versus-Statuses]]"]
tags: [requirement]
---

# Storage is words; display is check marks

Edwin: *"this is where I would like to see the check marks and not the states."*

The two are not in tension — the file wants an unambiguous token and the screen wants a checklist — and treating them as one field is what produced `[done]` rendered beside the label `Done`.

Criterion 2 is the one with teeth. Criteria 1 and 3 describe today's fix; the guard is what makes it hold, because the failure mode here is not a wrong rendering but a **silent** one: of the three sites, one was a dead comparison that removed styling and one was a `title` attribute.

## Acceptance criteria

- [x] One map, no direct reads. — evidence: `tests/test_acceptance_marks.py:513` asserts the four tables `MARK_GLYPH` / `MARK_TITLE` / `MARK_CLASS` / `VERDICT_FOR` are the only source, and `:281` pins the map itself.
- [x] A guard on raw words reaching a surface. — evidence: `test_no_surface_brackets_a_raw_mark_rather_than_its_glyph` (the bracketed form) **and `test_no_surface_renders_a_raw_mark_unbracketed_either`** (the unbracketed form). *(The second was added 2026-08-20: this criterion was ticked while `renderer.ts` drew `marked done` on a live surface, because the only guard checked brackets. See [[FEAT-0126]].)*
- [x] Storage unchanged. — evidence: `test_the_mark_vocabulary_reads_re_check` asserts the mark VALUE `rerun` is untouched: renaming it to fix a label would be a fleet-wide migration, not a label change.

## Independent review — fifth pass, 2026-08-20

Fresh context, separate session, `model:claude-opus-5`. **What was independent: the context** — this pass started from the notes and the diff at `c9c9563` and never saw the author's reasoning. **What was not: the model** — same family as the author, recorded in `reviewed_by` as provenance (ADR-0013). Verdict: **changes-requested**. Every claim below was executed or measured, not read.

**The title asserts something a surface deliberately violates.** *"…and no surface may render the stored form."* renderer.ts:9294 renders it: ``bits.push(`marked ${item.mark}`)`` puts `marked done` in the meta line of the release page's `Quiet` and `Stale evidence` groups, chosen by [[ISS-0244]] (*"`MARK_TITLE` is a sentence for a tooltip; the meta line wants the value"*). Criterion 2 carries the same over-claim — *"A guard fails if a raw mark word … reaches a rendered surface"* — and the guard is narrower than that: it matches only ``` `[${…mark…}]` ```. Executed: rendering the picker token as `` `${choice.mark}` `` instead of `MARK_GLYPH[choice.mark]` restores ISS-0211's defect in unbracketed form and the whole suite stays green but for the `dist/`-staleness hash check. See [[FEAT-0126]] for the run.

**Criterion 1's citation says something the line does not.** `tests/test_acceptance_marks.py:513` is a loop asserting each of `MARK_GLYPH` / `MARK_TITLE` / `MARK_CLASS` / `VERDICT_FOR` has an **entry for every mark in the fleet** — completeness, not *"the only source"*. The single-source property is what criterion 2's guard is for. `:281` does pin the map's literal forms, as claimed.

**Criterion 3 is cited to a test about something else.** *"Storage is unchanged: the notes still carry words"* is evidenced by `test_the_mark_vocabulary_reads_re_check`, whose two assertions are `MARK_MEANING["rerun"] == "needs re-check"` and `"rerun" in MARK_MEANING` — that one mark **value** was not renamed. Nothing in it reads a note or asserts what is written to one. The criterion may well hold; this is not the evidence for it.
