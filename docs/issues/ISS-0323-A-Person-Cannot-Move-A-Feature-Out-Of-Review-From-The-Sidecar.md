---
type: "[[issue]]"
id: ISS-0323
aliases: ["ISS-0323"]
title: "A person cannot move a feature out of review through the sidecar, so Deck's feature gate cannot offer Accept or Send back"
status: triage
phase: ""
owner: user:edwin
created: 2026-10-15
updated: 2026-10-15
source: ["[[project-os-deck#PHASE-0005]]", "[[project-os-deck#REFERENCE-COCKPIT-ADOPTION]]"]
reported_by: agent
question: ""
severity: medium
component: sidecar
parent: ""
related: ["[[project-os-deck#FEAT-0029]]", "[[project-os-deck#FEAT-0028]]"]
tests: []
---

# A person cannot move a feature out of review through the sidecar

**Deck's feature gate (project-os-deck FEAT-0029, its screen S7) cannot accept or send back a feature, because the sidecar offers no person-only transition for a feature.** `HUMAN_TRANSITIONS` in `src/project_os_cockpit/note_writes.py` has entries for requirements, ADRs, decisions, designs and issues, and none for features. `legal_actions` therefore lists no `review → done` or `review → doing` for a feature, and a `POST /api/notes/transition` asking for either is refused.

Deck now offers a transition only when the sidecar lists it, so both controls are drawn switched off with that reason. The opted-in `acceptance-run` records acceptance without changing the feature's status.

## Asked for

- Person-only transitions for a feature: `review → done` (accept) and `review → doing` (send back, with a reason), offered by `legal_actions` and guarded like the other human verdicts.

## Source

Requested in [[project-os-deck#REFERENCE-COCKPIT-ADOPTION]], "Requests to the cockpit", 2026-10-14, after Claude's review of project-os-deck FEAT-0029 found the gap against cockpit `ff08a0c`.
