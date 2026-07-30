---
type: "[[phase]]"
id: PHASE-015
aliases: ["PHASE-015"]
title: "Record hygiene (standing) — the documentation says what actually happened"
status: active
order: 15
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
goal: "A standing home for corrections to the record itself — a phase that says the wrong thing, an instruction that describes something that does not exist, a status that outlived its truth. No end date; it closes only if the record stops needing correcting."
features: []
requirements: []
issues:
  - "[[ISS-0074-Sixteen-Delivered-Notes-Stranded-In-The-Parking-Lot]]"
  - "[[ISS-0078-Downstream-Pilot-Was-Overtaken-And-CLAUDE-Md-Still-Claims-It]]"
depends: ["[[PHASE-013-Fleet-Surfaces]]"]
related: ["[[PHASE-014-Project-Inbox]]", "[[PHASE-999-Future]]", "[[ADR-0009]]"]
tags: [docs-system]
---

# Record hygiene (standing)

## This is a standing phase

Converted 2026-07-30, and it is the first application of the rule [[ISS-0077]] produced: *one long-lived phase per durable surface, that small fixes join, rather than a phase per request.*

It was `done` after [[ISS-0074]]. Reopening it rather than minting PHASE-020 for the next small records correction **is the mechanism working** — that issue measured nine phases in a day precisely because there was nowhere to put a small thing.

A standing phase has no end date. Its exit criteria below belong to the [[ISS-0074]] leg and stay ticked as that leg's record; the phase itself closes only if the record stops needing correcting.

## Goal

A `phase:` value answers a **plan-time** question — *which phase will deliver this?* — and nothing ever re-asks it as a **record** question — *which push shipped it?* After the work, "not planned yet" is not a stale value, it is a category error. So delivered work accumulates in the sentinel by construction, not by neglect, and 16 of the 19 notes naming `PHASE-999` here were terminal.

Small phase, and deliberately its own rather than folded into [[PHASE-014]]: that note is about the project inbox, and muddying a phase note written to be precise about what it delivered would be the same class of error this phase exists to correct.

## Scope

- **[[ISS-0074]]** — re-home the sixteen, from evidence rather than judgement; give the sentinel note its missing second exit; guard the corpus locally.
- **[[PHASE-014]]** is an *artifact* of this work, not scope: one of the sixteen had no phase that delivered it, so one had to be written.

## Out of Scope

- **The rule itself.** `LIFECYCLE.md`, `STATUSES.md` and `validate-docs.py` are template-owned and this repo holds the validator byte-identical ([[ISS-0026]]). The check is proposed upstream as `project-os-dev` ISS-0027; what lands here is a local guard, which is the same split [[ISS-0069]] took.
- **The rest of the fleet.** `your-trainer` (72 notes) and `project-os-dev` (42) have the same backlog. Correcting them is theirs to do once the rule is decided, and doing it now would be sixteen judgements times three repos with no check to hold them.

## Exit Criteria

- [x] No terminal note names the parking-lot phase — evidence: 3 notes name it, all non-terminal (`FEAT-0029` backlog, `TASK-0045` and `TASK-0065` deferred)
- [x] Every re-homing is justified by a link already in the note, or by a phase note written for it — evidence: the table in [[CHG-20260730-Phase-Hygiene]], 15 from `parent:` / `fixed_by:` / `implements:` / file location, 1 by [[PHASE-014]]
- [x] The sentinel note documents both exits — evidence: [[PHASE-999]] § "Two exits, not one"
- [x] The corpus cannot silently refill — evidence: `test_no_terminal_note_sits_in_the_parking_lot`, mutation-verified
- [x] The rule is filed where it can hold for every repo — evidence: `project-os-dev` ISS-0027

## Notes

**Found by a user reading the surface.** The phase strip drew sixteen `delivered` squares inside a phase titled "Future / Unphased" and no check anywhere reported it. That is the fourth time in a week that a rendering caught what validation could not — after [[ISS-0069]], [[ISS-0072]] and [[ISS-0073]] — and the first where the reader was Edwin rather than a test.

**Two spellings.** The corpus used both `[[PHASE-999-Future]]` and the bare `[[PHASE-999]]`. The first correction pass matched only the long form and stopped partway, which is the same near-miss [[PHASES.md]] already records for the never-existing `PHASE-999-Unscheduled`. The guard below matches on the resolved ID, not on either spelling.
