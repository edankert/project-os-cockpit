---
type: "[[issue]]"
id: ISS-0325
aliases: ["ISS-0325"]
title: "No guarded sidecar action sets a note's phase, so accepting a re-phase suggestion in Deck moves tickets on screen only"
status: triage
phase: ""
owner: user:edwin
created: 2026-10-15
updated: 2026-10-15
source: ["[[project-os-deck#PHASE-0005]]", "[[project-os-deck#REFERENCE-COCKPIT-ADOPTION]]"]
reported_by: agent
question: ""
severity: low
component: sidecar
parent: ""
related: ["[[project-os-deck#FEAT-0029]]", "[[project-os-deck#FEAT-0028]]"]
tests: []
---

# No sidecar action sets a note's phase

**Deck's re-phase screen (project-os-deck FEAT-0028, screen S4) suggests a phase for every ticket that names none, and accepting a suggestion can only move the tickets on screen.** No sidecar write sets one frontmatter field, `phase:`. On 2026-10-14 your-trainer had 987 tickets with no phase, 438 of them with a suggestion.

## Asked for

- A guarded, person-only write, for example `POST /api/notes/set-phase` with `{id, phase, mtime}`, that writes `phase:` on one note and refuses a phase the workspace does not have.

## Source

Requested in [[project-os-deck#REFERENCE-COCKPIT-ADOPTION]], "Requests to the cockpit", 2026-10-14 (project-os-deck TASK-0129).
