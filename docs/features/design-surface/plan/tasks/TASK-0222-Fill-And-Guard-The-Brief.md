---
type: "[[task]]"
id: TASK-0222
aliases: ["TASK-0222"]
title: "Fill this repo's brief, and report a placeholder brief upstream"
status: doing
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["[[REQ-0024-Brief-Is-Maintained]]"]
parent: "[[FEAT-0043-Design-Top-Level-Surface]]"
effort: "S"
depends: []
blocks: ["[[TASK-0223]]"]
related: []
tests: []
---

# Fill and guard the brief

## Definition of Done

- [ ] `LLM_BRIEF.md` in this repo states what the cockpit is, who it is for, and its shape — no `REPLACE ME`
- [ ] A `BRIEF-PLACEHOLDER` check reports a brief still carrying template placeholders, authored **upstream** and synced
- [ ] The check is a **warning, not an error** on first landing: ten repos would fail immediately, and a gate that turns the whole fleet red is a gate people disable
- [ ] Inversion-verified: fires on a placeholder brief, silent on a filled one, silent when there is no brief at all
- [ ] Fleet measured after the change, and the count recorded

## Steps

- [ ] Write this repo's brief from what the repo actually is, not from the template's prompts
- [ ] Add the check upstream in `project-os-dev`, propagate
- [ ] Inversion-test all three cases
- [ ] Record the fleet count

## Notes

Ordered first because **a view over an empty file is worse than no view.** Rendering "Purpose: REPLACE ME" as the first thing an agent reads every session would actively mislead, and would make the surface look broken on day one.

Warning rather than error is a deliberate call and worth stating: this check would fail 10 of 11 repos the moment it lands, including `project-os` itself. A gate that turns the whole fleet red teaches people to ignore the gate. It escalates once the fleet is filled in — the same dated-promotion shape ADR-0011 uses.
