---
type: "[[feature]]"
id: FEAT-0134
aliases: ["FEAT-0134"]
title: "The check note sheds the verdict — seven fields leave the schema, the template and the validator, and the note holds nothing platform-shaped"
status: backlog
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
goal: "The check note holds what the behaviour is, how it is grouped and how it gates — and nothing about who verified it, when, on what, or whether a machine covers it."
requirements: ["[[REQ-0053-The-Note-Holds-Nothing-Verdict-Shaped]]"]
tasks: ["[[TASK-0530-Remove-The-Seven-Fields-Upstream-First]]", "[[TASK-0531-The-Note-To-Ledger-Migration-Script]]", "[[TASK-0532-Fix-The-Splitter-Before-Anything-Migrates]]"]
related: ["[[ADR-0037-A-Verdict-Is-An-Event]]", "[[ISS-0216-The-Suite-Parser-Splits-On-Physical-Lines]]", "[[ISS-0198-Automation-And-Covered-By-Are-Empty-On-All-669-Checks]]"]
tags: [feature]
---

# Note = intent

## Goal

Remove `mark`, `verdict_date`, `verdict_reason`, `invalidated_by`, `automation`, `covered_by` and `evidence` from the acceptance test schema, the template and the validator. What is left is `tier`, `area`, `covers`, `level` and the body.

## Why this is cheaper than it looks, and where it is not

**Four of the seven are empty in 100% of the corpus** — `verdict_date`, `verdict_reason`, `invalidated_by`, `covered_by`, measured across 671 notes on 2026-08-19. Removing them costs nothing and loses nothing.

`covered_by` being empty is not neglect: [[ISS-0198]] closed with it deliberately empty because the 203 annotated bodies name 54 JVM classes and no `TST-*` id, and `cover_check` correctly refuses an unrunnable claim. That population is what [[FEAT-0138]] picks up.

**The two that carry data are `mark` (671) and `automation` (203 non-`manual`).** `mark` moves into the ledger. `automation` does not move anywhere — it becomes an observed `method:` on a run, and its current values are [[DES-0012]] D2's already-decided casualty. Its **203 prose annotations** are the seed for [[FEAT-0138]] and must be preserved before the field goes.

## Scope

- `SCHEMAS.md`, `TAXONOMY.md`, `TESTING.md`, `STATUSES.md`, `docs/__templates__/test.md`, `validate-docs.py` — **upstream first** ([[ADR-0030]] decision 6), then synced down.
- The migration script: strip the fields, emit the equivalent ledger entries, refuse to run twice, and list what it could not convert rather than skipping silently.
- **The splitter fix ([[ISS-0216]]) lands before any repo migrates again.** Six notes in `your-trainer` are already truncated by it; one body is the word `From`.

## Out of scope

- `covers:`. It stays — it is intent, and it is the gating axis [[ADR-0034]] and [[ADR-0032]] established.
- `tier:`. [[ISS-0208]] owns it.
- The 156 stranded checklist rows ([[ISS-0215]]) — they are not in the suite and this migration does not reach them.

## Acceptance

- [ ] No acceptance note in a migrated repo carries any of the seven fields.
- [ ] The validator refuses one that does, naming the ledger as the place it belongs.
- [ ] The migration is reversible from git and refuses a second run.
- [ ] The splitter parses a hard-wrapped bullet as one item, proved on a fixture, before any migration runs.
- [ ] `your-trainer`'s 203 automation annotations are preserved in a form [[FEAT-0138]] can seed from.
