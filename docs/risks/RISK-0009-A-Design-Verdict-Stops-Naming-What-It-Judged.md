---
type: "[[risk]]"
id: RISK-0009
aliases: ["RISK-0009"]
title: "A design verdict stops naming what it judged, so an approval given to revision 3 silently covers revision 6 — knowingly accepted by Edwin on 2026-09-12, with 'for now' in the sentence"
status: open
phase: "[[PHASE-999-Future]]"
owner: user:edwin
created: 2026-09-12
updated: 2026-09-12
source: ["Edwin, 2026-09-12: 'Drop the binding for now!'", "src/project_os_cockpit/note_writes.py:230", "[[ISS-0056-Offered-Design-Routes-To-Plan-Verdicts]]", "[[TASK-0375-Decide-And-Accept-On-The-Constraints-View]]"]
likelihood: medium
impact: medium
mitigation:
  - "Accepted deliberately rather than mitigated; the way back is stated below and is one task"
  - "The three existing design_revision values are left in their notes, so what was bound stays bound"
  - "The design-authoring skill says a verdict is given to what the note says today, and a material revision needs a new verdict"
related:
  - "[[FEAT-0148-One-HTML-Viewer]]"
  - "[[ISS-0056-Offered-Design-Routes-To-Plan-Verdicts]]"
  - "[[TASK-0375-Decide-And-Accept-On-The-Constraints-View]]"
  - "[[TASK-0615-Remove-The-Bench]]"
  - "[[REQ-0065-A-Design-Is-Markdown-First]]"
tags: [risk, design, review, accepted-tradeoff]
---

# A design verdict stops naming what it judged

## Description

Today a design's Accept writes two things: the verdict, and `design_revision` — the git commit of the artifact the reviewer was looking at, validated against real history. Retiring `/api/design/verdict` keeps the buttons and drops the second field. `note_writes.py:230` states the consequence in the words it was written in:

> A design accepted through `/api/notes/transition` gets `status: accepted` and no `design_revision` — so an approval given to revision 3 silently covers revision 6, which is the one way a design review is worse than no review at all.

That is the hazard [[ISS-0056-Offered-Design-Routes-To-Plan-Verdicts]] and [[TASK-0375-Decide-And-Accept-On-The-Constraints-View]] exist for, and this phase re-opens it on purpose.

## Accepted, by whom, and in what words

**Edwin, 2026-09-12: "Drop the binding for now!"** — chosen from three options after he challenged the plan's claim that design verdict buttons were being retired. His challenge was correct and the plan was wrong; see the correction note in [[FEAT-0148-One-HTML-Viewer]].

**"For now" is load-bearing and is why this is a risk note rather than a closed decision.** He accepted a known trade-off with an explicit expectation of revisiting it, not a permanent position. Nothing here should be read as saying revision binding was a bad idea.

## What actually changes

- `VERDICT_ENDPOINTS` loses its `design` entry, so the generic transition path stops refusing the type.
- `DESIGN_REVIEW_FIELDS` and the writing of `design_revision` go, along with the refusal message that names the old endpoint.
- **Existing `design_revision:` values stay in their notes.** Three designs carry one — `project-os-cockpit` DES-0002 and DES-0004, and DES-0009 — and a note is never rewritten to erase what was true when it was written.

## Why the old protection was weakening anyway

`design_revision` names a commit **of the artifact file**. Markdown-first means a design often has no artifact file, so there is no artifact revision to bind to. The binding would have needed widening regardless of this decision — from "the commit of the `.html`" to "the commit of whatever the design is". Retiring it is therefore giving up a protection that already did not cover the case the phase is making normal, rather than giving up one that worked.

## The way back

A verdict names the commit of **whatever the design is** — the note, or the note and its page together when there is one — instead of the artifact file. That is the option Edwin declined on 2026-09-12, and it is what "for now" leaves open. It is roughly one task: widen what the revision means, write it from the generic transition path, and keep the git validation that already exists.

## Triggers

- A design at `accepted` whose note has been materially edited since its `review_date`, with no new verdict. This is the failure happening, and it is greppable.
- Someone citing a design's `accepted` status as approval for something the note did not say at the time it was accepted.
- A second design review disagreeing with an earlier one without either naming what it read.

## Closing condition

Closes when a verdict names what it judged again, or when Edwin says the trade-off is permanent — in which case this becomes a decision note rather than an open risk. It does **not** close because the bench was removed.

## Re-homed to [[PHASE-999-Future]] (2026-09-12)

PHASE-042 closed and this risk did not, which is the honest pair: Edwin accepted the trade-off knowingly — *"Drop the binding for now!"* — and "for now" is a decision to revisit, not a problem solved. A phase may not close with an unresolved child, and `deferred` would not resolve it either, so it is parked where open work with no scheduled home belongs.

It comes back to a real phase the day someone wants a design verdict to name what it judged again. The way back is one task, written in this note.

## Corrected 2026-09-12 (independent review)

This note said the change "keeps the buttons and drops the second field", which understates it. Two corrections:

- **From the note's actuator row, Accept writes a status and no verdict at all** — not "one field fewer". That is how every type behaves through `stamp_transition`, and it is not a change this work made; the bench's endpoint was the only path that wrote a verdict from a button.
- **From the review desk, a design's decision does write a verdict**, and since this review it writes `approved` / `changes-requested` rather than the proposal vocabulary. The same review found the desk path would also have moved a *settled* design — writing `cancelled` over `implemented`, which is ISS-0056's own example — because the guard that prevented it lived inside the deleted endpoint. Both are fixed and tested (`test_tests_view.py`).

What this risk records is unchanged: no verdict names the revision it judged.
