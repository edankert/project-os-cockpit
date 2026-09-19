---
type: "[[feature]]"
id: FEAT-0154
aliases: ["FEAT-0154"]
title: "Subject threads — a feature, design, issue or release opens as a header card, a timeline of what happened and the note, with the agent's work folded"
status: backlog
phase: "[[PHASE-045-The-Cockpit-In-Layers]]"
owner: user:edwin
created: 2026-09-17
updated: 2026-09-17
source:
  - "[[DES-0015-The-Cockpit-In-Layers]], option B, recommended last"
  - "Edwin 2026-09-17: 'think of this as an Apple design or the way the OpenAI ChatGPT and Claude online and desktop tools have been constructed'"
goal: "A subject opens on its state and its next action, then on what happened to it in order, then on its note; the machine's work on it is one line a person can open, and the raw frontmatter is behind a fold."
requirements: []
tasks: []
release: ""
acceptance_exception: ""
acceptance: ""
design: "[[DES-0015-The-Cockpit-In-Layers]]"
related:
  - "[[FEAT-0152-Home-First]]"
  - "[[FEAT-0153-Flows-As-Views]]"
  - "[[DES-0005-The-Actuator-Grammar]]"
  - "[[FEAT-0052]]"
  - "[[project-os-deck#REFERENCE-SURFACE-ARCHITECTURE-OPTIONS]]"
---

# Subject threads

**Not started, not yet accepted, and possibly not this repository's to build.** This is option B of [[DES-0015-The-Cockpit-In-Layers]], the largest renderer change of the three. The phase note records that Deck may be its better home; if Edwin decides so, this note is `superseded` by a Deck note and [[PHASE-045-The-Cockpit-In-Layers]] shrinks to the other two.

## Goal

Layer L3 of the design. A feature, design, issue, release or check opens as a thread. The header card distils the frontmatter: status, phase, owner and date on one line, the goal as one sentence, the relationships as labelled bars, the next action as the registry's verb. Then "what happened": the history payload filtered to this subject, newest first, with agent sessions collapsed into one line the way Claude's desktop app collapses tool calls. Then the note body. The right pane keeps its context groups folded to those with a state, and slides in for an artifact. The sidebar lists subjects by recency and need rather than by type.

## Scope

- A header card per subject type, built from the fields the note renderer already strips: feature, design, issue, release, test.
- A timeline from the history payload, which already carries note ids per transition, joined to commits, verdicts and review fields; sessions from the sessions payload, folded.
- The actuator row of [[DES-0005-The-Actuator-Grammar]] moves into the header card unchanged; no verb is added or renamed.
- The frontmatter table stays, behind a fold.
- Out: any write path; the note renderer itself (Markdown is still parsed only by the sidecar); the pane architecture.

## Acceptance

- A feature's first screen shows its goal, three bars and its next action without scrolling, and the frontmatter is not on screen one.
- The timeline for a subject lists the same transitions History lists for it, in the same order.
- An agent session on a subject is one folded line until opened, and the strip still shows the live state.
- Every actuator on the header card is one the note offered before.
- The capability register names the new rows.

## Links

- Design: [[DES-0015-The-Cockpit-In-Layers]], Plate 4 and the as-built feature note capture.
- Phase: [[PHASE-045-The-Cockpit-In-Layers]], decision D5.
- Plan: `plan/PLAN.md`.
