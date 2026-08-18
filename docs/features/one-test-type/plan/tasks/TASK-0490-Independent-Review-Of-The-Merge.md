---
type: "[[task]]"
id: TASK-0490
aliases: ["TASK-0490"]
title: "The independent review of the whole programme, against the corpus rather than against the plan"
status: backlog
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
source: ["[[FEAT-0119-The-Merge-Migration]]"]
parent: "[[FEAT-0119-The-Merge-Migration]]"
effort: M
depends: ["[[TASK-0485-Backfill-Automation-From-The-Prose]]", "[[TASK-0488-Drop-The-Feature-Tests-Field-And-The-Path-Fallback]]"]
blocks: []
related: []
tests: []
---

# Independent review of the merge

Owed under QUALITY.md: two ADRs, four features reaching `done`, new `TST-*` notes and a `CHG-*`. Clean context, from the notes and the diff — never this session's reasoning ([[project-os-dev#ADR-0013]]).

**Review the result against the corpus, not this plan.** The plan's own figures — 669, 203, 15 of 60, 20 of 61, zero inbound `CHK-*` references, 10 to backfill — are all re-derivable, and the last review of this subject corrected five figures in the note it was reviewing. Re-derive them.

Specific questions worth putting to it: did the badge move in any repo; is the twelve-tag delta on `your-trainer` genuinely unchanged; is there any surviving predicate on the retired type; did the VERIFY inversion change which violations fire; and is [[REQ-0039-A-Covering-Test-Settles-The-Check]] actually satisfied — how many checks were discharged by a covering test, measured, and not how many *could* be.

Done when: a verdict is recorded on the features and on this note, and anything it returns as `changes-requested` is fixed or filed rather than argued with.
