---
type: "[[issue]]"
id: ISS-0324
aliases: ["ISS-0324"]
title: "The sidecar refuses an agent only on acceptance-run; decide and mark-check accept any named reviewer"
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

# The sidecar does not refuse an agent on decide or mark-check

**A design verdict (`/api/notes/decide`) and an acceptance-check result (`/api/notes/mark-check`) are accepted from any non-empty name, including an `agent:` one.** `stamp_decision` in `note_writes.py` raises only on a missing reviewer, and `record_verdict` only requires `by`. Only `stamp_acceptance_run` refuses an `agent:` witness without a charter.

project-os-deck refuses any identity that is not `user:` before it sends, so Deck never writes such a verdict as an agent. But the guard belongs in the sidecar, where every client meets it; Deck's FEAT-0029 had to narrow its criterion ("the same verbs from an agent session are refused") because of this.

## Asked for

- `decide` and `mark-check` refuse an `agent:` reviewer or tester, as `acceptance-run` does, unless a charter allows it.

## Source

Requested in [[project-os-deck#REFERENCE-COCKPIT-ADOPTION]], "Requests to the cockpit", 2026-10-14; found by Claude's review of project-os-deck FEAT-0029 against cockpit `ff08a0c`.
