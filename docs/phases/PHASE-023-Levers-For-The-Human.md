---
type: "[[phase]]"
id: PHASE-023
aliases: ["PHASE-023"]
title: "Levers for the human — the cockpit writes the record it renders, wherever the transition is the human's to make"
status: done
order: 23
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
goal: "Every judgment the docs contract assigns to the human — approving, accepting, triaging, answering — becomes an action in the cockpit, so governing the record stops requiring an agent as intermediary."
features:
  - "[[FEAT-0059-The-Write-Service-Widens]]"
  - "[[FEAT-0060-Transitions-And-Ticks-On-The-Note]]"
  - "[[FEAT-0061-Quick-Capture-And-Triage]]"
  - "[[FEAT-0062-Desk-Resolution-Flows]]"
requirements:
  - "[[REQ-0026-Only-Human-Owned-Transitions]]"
  - "[[REQ-0027-Every-Write-Guarded]]"
issues: []
depends: ["[[PHASE-022-Completed-Work-Gets-Quieter]]"]
related: ["[[DES-0005-The-Actuator-Grammar]]", "[[RISK-0005-The-Write-Surface]]"]
tags: [write-back, governance]
---

# Levers for the human

## Where this came from

Edwin asked for a full review of the cockpit as a tool for a human who governs through the docs rather than the code (2026-08-03). The review's structural finding: **the human has no levers.** Every transition in STATUSES.md's ownership table is owned by *agent*; the cockpit's only actuator is asking an agent in the terminal. Yet some judgments are inherently the human's — approving a requirement, accepting a design, triaging an issue, answering a question — and the tool renders them without letting the human make them.

The two-day PHASE-022 session was the evidence: twelve corrections, all governed through chat because no surface could receive them.

## The line this phase moves, and the line it keeps

PHASE-007 drew "the cockpit is a viewer". ADR-0007 crossed it exactly far enough to *record a decision a human made in the UI* — `note_writes.py` exists, with field allow-lists, per-type decide-transitions, mtime preconditions, loopback-only access, atomic format-preserving writes.

This phase **widens that door without changing its principle**: every new write records a human judgment. Nothing here lets the cockpit (or a LAN reader) perform an *agent's* transition — close-out stays the agent's job, gates stay the validator's.

## Scope

[[FEAT-0059]] widens `note_writes` (transition table as data, criteria ticks, issue creation). [[FEAT-0060]] puts the actions on the note. [[FEAT-0061]] gives thoughts an entry point and `triage` a surface. [[FEAT-0062]] closes the desk's two dangling flows (changes-requested → re-review; question → answer).

Design: [[DES-0005]] — the actuator grammar.

## Out of Scope

- **Agent-owned transitions.** The ownership table's agent column stays agent-only; the cockpit refuses them by construction, not by convention.
- **Prose editing.** Ticking a criterion writes a line; nothing edits paragraphs. The notes' author remains whoever writes them.
- **SNAPSHOT.yaml.** ADR-0009 stands: sync-snapshot propagates at pre-commit; the cockpit never touches it.

## Exit Criteria

- [x] Every transition in STATUSES.md's user-ownable set is performable from the note that carries it — evidence: the actuator row on the note ([[FEAT-0060]]), built from `GET /api/notes/actions` with no local list; `test_every_status_in_the_table_exists_in_the_vocabulary` and `test_the_actuator_row_declares_no_vocabulary` guard it (user:edwin, 2026-08-11)
- [x] No agent-owned transition is reachable from any surface — evidence: `test_an_agent_owned_transition_names_the_rule` — the refusal is server-side and quotes [[REQ-0026]], and `stamp_transition` is keyed on the note's CURRENT status so a stale renderer cannot replay a stale offer (user:edwin, 2026-08-11)
- [x] A thought becomes a triaged issue without composing a prompt — evidence: ⌘N quick capture writes an issue at `triage` through `create_issue` ([[FEAT-0061]]); capture is deliberately dumber than intake — a title now beats a paragraph never (user:edwin, 2026-08-11)
- [~] The changes-requested register can reach zero through the desk alone — **reconciled, not delivered.** The desk it names was retired by [[ADR-0020]] and removed by [[FEAT-0090]], and [[FEAT-0062]], which would have built the re-review flow, was **cancelled** on Edwin's decision ([[ISS-0126]], 2026-08-11). Measured that day: 10 `changes-requested` notes, **0** with a non-terminal subject — the register is already at zero, and the criterion asks for a route to zero through a surface that no longer exists. The inverse case is preserved by [[ISS-0121]]'s fix and surfaces in the view owning the note's type
- [x] All writes remain loopback-only and mtime-guarded — evidence: [[RISK-0005]] closed 2026-08-11. `test_every_note_mutating_endpoint_requires_loopback` parses the POST dispatch table — 21 routes — so an endpoint that forgets the guard fails by existing; `test_a_stale_mtime_refuses_and_writes_nothing` and `test_a_stale_mtime_refuses_the_tick` cover the precondition. [[REL-0001]]'s pass drove 10 of 10 over a real LAN interface for 403s (user:edwin, 2026-08-11)
