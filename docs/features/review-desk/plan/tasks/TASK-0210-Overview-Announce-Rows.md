---
type: "[[task]]"
id: TASK-0210
aliases: ["TASK-0210"]
title: "Overview announce rows — typed decide/review/answer/run rows in Waiting-on-you deep-linking into ~review"
status: done
phase: "[[PHASE-008-State-And-Review-Surfaces]]"
owner: user:edwin
created: 2026-07-26
updated: 2026-07-26
source: ["https://claude.ai/code/artifact/3e6b4313-66e9-4fca-b11b-97c3d7a1d1be"]
parent: "[[FEAT-0041-Review-Desk]]"
effort: ""
due: ""
depends: ["[[TASK-0200]]", "[[TASK-0206]]"]
blocks: []
related: ["[[FEAT-0040-Overview-Rework]]"]
tests: []
---

# Overview announce rows

## Definition of Done

- [x] Review-queue items surface in the overview's Waiting-on-you list as typed rows — kind tag (decide / review / answer / run), item ID, title, status/age chip — matching the dossier's plate E exhibit.
- [x] Each row deep-links into ~review at the right target (`~review/<ID>`, `~review/<TST-ID>/run`); no review flow ever happens on the overview itself.
- [x] Rows obey the Waiting-on-you ordering and the "All clear" empty state from TASK-0200; queue rows and durable-state rows compose in one list without double-counting (e.g. TST-0011 appears once, as a `run` row, not also as a bare ready-test row).
- [x] The announce rows and the Review badge (TASK-0206) agree on counts.

## Steps

- [x] Extend TASK-0200's Waiting-on-you row model with the typed kinds + deep links.
- [x] De-duplication rule between queue-derived and state-derived rows.
- [x] Count-consistency check with the badge.

## Notes

This is the only hard cross-feature coupling between FEAT-0041 and FEAT-0040 (TASK-0211's panel coordinates with the reworked phase detail but does not require it) — the two features are otherwise independently shippable. If FEAT-0040 has not landed yet, this task waits; the desk works without announcement (badge only).
