---
type: "[[issue]]"
id: ISS-0031
aliases: ["ISS-0031"]
title: "Review desk: queued plans could not be reviewed, and no lone queued note could be decided"
status: fixed
severity: medium
owner: user:edwin
created: 2026-07-26
updated: 2026-07-26
component: review-desk
phase: "[[PHASE-008-State-And-Review-Surfaces]]"
source: ["user-report:2026-07-26"]
parent: "[[FEAT-0041-Review-Desk]]"
related: ["[[FEAT-0041-Review-Desk]]", "[[TASK-0206-Review-Virtual-Page]]", "[[TASK-0207-Proposal-Set-Review]]", "[[ADR-0007-Planning-Artifact-Approval-Gate]]"]
tests: ["[[TST-0021-Review-Desk]]"]
---

# Plans and lone notes could not be reviewed

## Problem

Reported while using the desk on the day it shipped: "still many plans I am not able to review… for instance PLAN-FEAT-0007, PLAN-FEAT-0040 and PLAN-FEAT-0041", then "also ADR-0007 I am not able to review."

Both symptoms were real. They had different causes.

## Cause

**1. Plans should never have been queued.** `STATUSES.md`'s `[[plan]]` contract says a plan's status *follows its parent feature* and is advanced at close-out. `draft` on a plan therefore means "the feature hasn't started", not "a human owes this a decision". TASK-0206 mapped `plan: draft` into `QUEUE_INTAKE_STATES` alongside genuine intake states, which asked for a review nobody could perform. Plans also carry no `id:` by contract, so a queue row had nothing stable to address them by — the three that *were* clickable were clickable only because they carried the forbidden ID.

**2. Lone queued notes had no actions at all.** TASK-0207 built Accept / Request changes / Reject for proposal *sets* backed by a ledger request. A single queued note — a proposed ADR, a draft requirement — fell to `buildSingleNoteReview`, which rendered a header and an "Open note ↗" button and nothing else. Underneath the missing buttons was a deeper gap: `ALLOWED_TRANSITIONS` permitted exactly one status move (`cancelled`), so even with a button there was no way to perform `proposed → accepted`. The desk could show you a decision and not let you take it.

## Fix

1. `plan` removed from `QUEUE_INTAKE_STATES`, with the contract quoted at the removal so it is not re-added.
2. New `DECIDE_TRANSITIONS` map and `stamp_decision()` — per-type lifecycle moves drawn from each type's own vocabulary: ADR `proposed → accepted`, declined as `superseded`; requirement `draft → approved`, declined as `cancelled`. Gate-bearing types (test, change) are refused, as they are on the review path.
3. New `POST /api/notes/decide`, loopback-only, with the same field allow-list discipline as the other mutations.
4. Decide buttons on the single-note view, labelled from the type's vocabulary.

**An ADR is never "rejected".** `STATUSES.md` is explicit that a decision not taken is deleted or superseded, because a rejected proposal worth keeping is worth recording as the alternative it lost to. The decline button therefore says *Supersede*, not *Reject* — the UI follows the vocabulary rather than imposing a generic yes/no on it.

## Verification

[[TST-0021-Review-Desk]] gains five tests: plans absent from the queue, ADR accept, ADR decline-is-supersede (asserting `rejected` never appears), requirement approve, and refusal for types the desk does not own. Confirmed against the live corpus: the queue fell from 6 items to 3, and ADR-0007 now offers *Accept decision* / *Supersede*.

## What it says about the desk

Both bugs share a shape: the desk was built around the proposal-set flow and treated everything else as a variant of it. A plan is not a small proposal; a lone ADR is not a one-item set. Queue membership was decided by a status filter without asking, per type, *what decision is actually pending and who owns it* — the question the fix answers explicitly with `DECIDE_TRANSITIONS`.

## Follow-up: the decision surface showed no content (2026-07-26)

Reported immediately after the first fix: *"To be able to approve the requirements, I will need to be able to see what to approve, I can still not see this?"* — and then the same for ADRs.

Correct, and a plain oversight. The decide buttons landed on a page that rendered a header, the buttons, and nothing else. Approving a requirement means reading its acceptance criteria; accepting an ADR means reading the decision, its context and the alternatives it beat. The page asked for a judgement while withholding everything the judgement rests on.

The single-note view now mounts the note itself via `/api/render` — the same call the centre pane makes, so the metadata strip, wikilinks and checkboxes behave identically and the reviewer reads the real note rather than a summary of it. Links inside the mounted subtree are wired to `navigateTo` explicitly, since the centre pane's delegated handler only covers `#doc-view`.

The proposal-set view had the same flaw one level up: five task rows with tick-boxes and no content, so a *set* was approved as blind as a lone note. Each row now carries an expander that loads its note inline on first open, plus a "Show all notes" control — reading five notes one click at a time is only marginally better than not reading them.

The through-line with the two original defects is the same: the desk was built as a queue and then as a set of actions, without ever asking what a reviewer needs in front of them to act. A decision surface has to show what is being decided.

