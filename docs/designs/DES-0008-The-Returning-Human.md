---
type: "[[design]]"
id: DES-0008
aliases: ["DES-0008"]
title: "The returning human — the first minute back: what happened, what needs you, what shipped"
role: proposal
status: "accepted"
phase: "[[PHASE-026-The-Returning-Human]]"
owner: user:edwin
created: 2026-08-03
updated: "2026-08-03"
source: ["Review 2026-08-03: nothing in the cockpit is addressed to the person who was away while agents worked; the landing's NEEDS-YOU cards know only about waiting terminals"]
asset: "DES-0008-returning-human.html"
implements: []
supersedes: ""
superseded_by: ""
reviewed_by: "user:edwin"
review_date: "2026-08-03"
review_verdict: "plan-accepted"
related: ["[[FEAT-0071-Since-You-Looked]]", "[[FEAT-0072-The-Release-Surface]]", "[[DES-0001-Overview-Redesign]]"]
---

# The returning human

## The watermark

Server-side, `.cockpit/last-seen.json` per workspace — one human per cockpit, and server-side survives the renderer's storage being cleared. Moved only by an explicit **Caught up** action, never by merely opening the app: presence is not attention, and a watermark that moves itself turns the digest into a slot machine.

## The digest

Derived entirely from surfaces that exist: `history_payload` (status transitions since the watermark), the review registers (verdicts landed, questions asked), the acceptance queue (PHASE-024). Two placements:

1. **The landing card**, one line under each workspace: `since Thu · 14 transitions · 2 need you` — the NEEDS-YOU cards widened from "terminal waiting" to "anything waiting".
2. **A band atop the overview** when the watermark is behind: the transitions grouped exactly as History groups them, newest first, with the *needs-you* items (triage, questions, acceptance, changes-requested) lifted above the merely-informational. `Caught up` sits at its end — reading to the bottom is what being caught up means.

No notifications, ever. Pulled on arrival; the tool must not follow the human away.

## The release card

The overview record column gains `UNRELEASED · N`: features `done` since the last REL note (or ever, when none exists), in the record grammar. Opening it offers `Draft release note` — template-filled with the unreleased list, `status: draft`, for the actuator row to advance. On the REL note itself, the acceptance-tests gate finally renders: unchecked Tier 1/2 boxes listed with the template's own words — "a release is blocked while any Tier 1/2 test is unchecked" — as a warning band. The contract has existed since the template was written; this is its first surface.

## One voice (the sweep's rules)

- Empty states: one sentence pattern everywhere — *what this pane shows, and the shortest path to having some*. ("No issues yet — ⌘N captures one.")
- The collapse-completed eye: retire it if, after PHASE-022's per-card defaults, its analytics show no use; a control that duplicates defaults is two mechanisms for one idea, which is how the pill got wrong twice.
- The deliberate exceptions — the desk's headings (obligations, not collections) and the Library's file rows (files, not lifecycle notes) — written into [[DES-0002]] so the next session inherits the reasoning, not just the appearance.
