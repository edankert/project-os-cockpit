---
type: "[[task]]"
id: TASK-0222
aliases: ["TASK-0222"]
title: "Fill this repo's brief, and report a placeholder brief upstream"
status: done
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

- [x] `LLM_BRIEF.md` in this repo states what the cockpit is, who it is for, and its shape — no `REPLACE ME` — evidence: rewritten from what the repo is, not the template's prompts; 0 placeholders
- [x] A `BRIEF-PLACEHOLDER` check reports a brief still carrying template placeholders, authored **upstream** and synced — evidence: `validate_brief()` in `validate-docs.py`, authored in project-os-dev and synced to all 11 repos
- [x] The check is a **warning, not an error** on first landing: ten repos would fail immediately, and a gate that turns the whole fleet red is a gate people disable — evidence: exit 0 on a placeholder brief; 9 repos warn, 0 errors anywhere
- [x] Inversion-verified: fires on a placeholder brief, silent on a filled one, silent when there is no brief at all — evidence: 5 cases — absent (silent), placeholder (warns), filled (silent), case/separator variants (`replace me`, `Replace_Me`, `REPLACE-ME` all caught), and exit code 0
- [x] Fleet measured after the change, and the count recorded — evidence: **9 of 11 warn, 2 clean.** Before: 10 of 11 unfilled and nothing reported it.

## Steps

- [x] Write this repo's brief from what the repo actually is, not from the template's prompts
- [x] Add the check upstream in `project-os-dev`, propagate
- [x] Inversion-test all three cases
- [x] Record the fleet count

## Result

The brief now says what the cockpit is: four questions it answers, the invariants that matter (loopback-only mutations, one vocabulary one source, guarded write-back, the machine gathers and the human decides), and a **"Things that will surprise you"** section for the traps that cost real time here — `tools/` being template-owned, the validator shipping twice, `statuses.py` keeping retired values deliberately.

It also carries the two failures from this week as fast-failure checks, because both cost an hour and both are invisible from the symptom: *edited the renderer and the UI looks unchanged* (stale bundle) and *a payload looks right but the surface is empty* (unreachable route).

**Fleet: 9 of 11 warn, 2 clean, 0 errors anywhere.** Warning rather than erroring is what makes that tolerable — a gate failing ten of eleven repos on day one teaches people to disable the gate.

## Notes

Ordered first because **a view over an empty file is worse than no view.** Rendering "Purpose: REPLACE ME" as the first thing an agent reads every session would actively mislead, and would make the surface look broken on day one.

Warning rather than error is a deliberate call and worth stating: this check would fail 10 of 11 repos the moment it lands, including `project-os` itself. A gate that turns the whole fleet red teaches people to ignore the gate. It escalates once the fleet is filled in — the same dated-promotion shape ADR-0011 uses.
