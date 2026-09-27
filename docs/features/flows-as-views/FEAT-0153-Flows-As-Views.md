---
type: "[[feature]]"
id: FEAT-0153
aliases: ["FEAT-0153"]
title: "Flows as views — the navigator's modes become Home, Design, Build, Verify and Issues, each ordered by state with finished work folded to a count"
status: backlog
phase: "[[PHASE-045-The-Cockpit-In-Layers]]"
owner: user:edwin
created: 2026-09-17
updated: 2026-09-27
source:
  - "[[DES-0015-The-Cockpit-In-Layers]], option A, recommended second"
  - "Edwin 2026-09-17: the flows are 'design + review, implementation, verification and issue reporting/triage'"
goal: "Each of the four flows has one view that lists its subjects by state, needs you first and finished work folded to a count, so a flow's first screen shows no closed phase and no fixed issue unless the reader opens the fold."
requirements: []
tasks: []
release: ""
acceptance_exception: ""
acceptance: ""
design: "[[DES-0015-The-Cockpit-In-Layers]]"
related:
  - "[[FEAT-0152-Home-First]]"
  - "[[FEAT-0154-Subject-Threads]]"
  - "[[ADR-0020-Obligations-Live-With-Their-Subject]]"
  - "[[ADR-0028-Work-Has-Three-Phases]]"
  - "[[FEAT-0102-Publication-Becomes-A-View]]"
  - "[[DES-0012-Tests-In-Two-Flows]]"
---

# Flows as views

**Not started, not yet accepted, and it opens on a decision.** This is option A of [[DES-0015-The-Cockpit-In-Layers]]. It leaves `backlog` only when the design is accepted and D2 is decided, because D2 narrows [[ADR-0028-Work-Has-Three-Phases]], which gave publication its own view on 2026-08-16.

## Goal

Layer L2 of the design. The top bar's modes become Home, Design, Build, Verify and Issues, with text labels beside the icons. Each view's navigator and landing page carry the same sections in the same order: what needs you, what is in flight, what is queued, and what is finished folded to a count and fetched only when opened. A phase is a heading inside the queue, not a container for everything ever done. The Intent view's standing documents become Design's last fold. Verify's cards each name their scope, so the tests view stops saying "Nothing owed" beside a navigator saying "6 of 36 outstanding".

## Scope

- The navigator payload in `cockpit.py` gains a state-first grouping per view, with terminal groups sent as counts and a route to expand one group on demand. Measured today: the features navigator sends 43 groups here and 30 on your-trainer, of which 27 and 14 are closed phases; the issues navigator sends 293 and 416 rows with its severity groups listed twice.
- The Design view: Awaiting you, Offered, Drafting, Accepted and being built, Implemented folded, About this project folded and last.
- The Build view: Approve, Now, Next grouped by the active phase only, other phases folded by name, Done since the last release folded, unattached items folded.
- The Verify view: This release (owed checks by screen, settled bar, Test, Settle, coverage on one line), In flight (the focus feature's tests), Automated (last result or "no run recorded"), Retired folded.
- The Issues view: Triage queue, Open by severity as a stacked bar with the high rows first, Fixed since the last release folded, Deferred and Declined folded. A "Triage next" flow walking the queue one issue at a time with Accept, Defer, Decline and Duplicate of (D4).
- Where the publication ladder lives is D2's answer, not this note's.
- Out: subject pages ([[FEAT-0154-Subject-Threads]]), any write path, mode 1.

## Acceptance

- A flow view's first screen shows no closed phase and no fixed issue unless a fold is opened, on every repository the shell discovers.
- Each view's navigator payload reads under 30 KB before a fold is opened, measured on your-trainer.
- The badge on each mode button equals the count of the view's Needs you section, as [[ADR-0020-Obligations-Live-With-Their-Subject]] requires.
- Every number in Verify names its scope.
- The capability register names the new and changed rows, and the retired ones keep their keys.

## Links

- Design: [[DES-0015-The-Cockpit-In-Layers]], Plates 3, 5, 6 and 7, and the "four flows, layer by layer" table.
- Phase: [[PHASE-045-The-Cockpit-In-Layers]], decisions D2 and D4.
- Plan: `plan/PLAN.md`.
