---
type: "[[issue]]"
id: ISS-0127
aliases: ["ISS-0127"]
title: "The intent charter is scheduled last because delegated acceptance reads it — but nine phases need something to be checked against now, and nothing exists to check them against"
status: triage
phase: ""
owner: user:edwin
created: 2026-08-10
updated: 2026-08-10
source: ["Session 2026-08-10: reviewing all open phases for implementation order, Edwin asked what to use as a goal for the whole plan"]
severity: medium
component: "planning"
parent: ""
related: ["[[FEAT-0077-The-Intent-Charter]]", "[[TASK-0333-The-Charter-Note]]", "[[DES-0003-Intent-Page-And-Claims-Board]]", "[[PHASE-027-The-Standing-Worker]]", "[[REL-0001-The-Human-Has-Levers]]", "[[ADR-0009-The-Principal-Is-A-Role]]"]
tests: []
---

# The charter is scheduled by its consumer, not its value

## Problem

[[FEAT-0077]] produces *"a durable charter — goals, non-goals, taste constraints"*. It sits in [[PHASE-027]], the last and most speculative phase, because that is where its **consumer** lives: a delegated principal judging acceptance needs the asking written down.

That is a reason to have it by PHASE-027. It is not a reason to *not have it before*.

Nine phases and roughly 85 open tasks are currently ordered against each other with **no written statement of what the tool is for**. Every scoping decision is therefore argued from measurement, one at a time.

## Evidence: what "no charter" costs

Measured on this session, 2026-08-08 to 2026-08-10. A single line of enquiry — "add a kanban view" — produced:

1. A kanban on the overview, refuted by measurement (1 in-flight work item here, 77 fleet-wide)
2. A board on the review desk ([[DES-0010]], [[FEAT-0082]]) — designed, drawn in five plates, **superseded two days later**
3. The desk retired entirely ([[ADR-0020]])

Every step was decided from evidence and every step was right on the evidence it had. But a design was authored and superseded inside 48 hours, and the thing that would have caught it is a statement of what the surfaces are *for* — checked against before drawing, not after.

That is the cost, and it is not an argument about tidiness: it is one artifact's worth of work, from one question, in three days.

## Why this is not simply "do PHASE-027 sooner"

[[PHASE-027]] is the standing worker — delegation, escalation, leases. It is the biggest bet in the plan and correctly last. Only **one** of its parts is needed early, and only for a different purpose than the phase intends: [[TASK-0333]], the charter note itself.

[[TASK-0334]] (delegated acceptance, charter-bound) and the rest of the phase stay where they are. This is a re-homing of one task, not a re-ordering of a phase.

## What the charter would already say

The thesis is latent in the record and could be drafted from it — [[ADR-0009]] (the principal is a role, not a person), [[ADR-0020]] (obligations live with their subject), [[REQ-0026]] (only human-owned transitions), and [[PHASE-023]]'s founding finding that *the human has no levers*. Something near:

> The cockpit is the surface through which a person governs a project they did not write. It renders the record, shows what the record owes, and lets that person discharge exactly the judgments that are theirs — never the agent's.

**But the charter is the one artefact here that cannot be derived.** Everything else this session produced came from measurement — 94% of standing documents stale, zero questions ever asked, 39 issues at triage with a 56-day median. Goals, non-goals and taste constraints are a position, not a finding. A draft from the record is an editable starting point and nothing more; the charter is only worth having if it is Edwin's.

## Next Actions

- [ ] Re-home [[TASK-0333]] (the charter note) out of [[PHASE-027]] — to [[PHASE-030]], or standing alongside [[REL-0001]] as the goal that release serves
- [ ] Draft it from the record so there is something to react to rather than a blank page
- [ ] Edwin owns the non-goals in particular — those are what a charter is actually for, and the record contains almost none of them
- [ ] Leave [[TASK-0334]] and the rest of [[PHASE-027]] where they are
- [ ] Once it exists, check the open phases against it — the test of a charter is whether it changes an ordering decision, and if it changes none it was not worth writing
