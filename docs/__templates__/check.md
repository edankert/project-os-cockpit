---
type: "[[check]]"
id: CHK-0000
aliases: ["CHK-0000"]
title: ""
status: active          # LIFECYCLE only: draft | active | retired. Ticking never touches this.
owner: unassigned
created: 2026-01-27
updated: 2026-01-27
tier: 1                 # 1 feature check · 2 regression check · 3 verification check for one build
area: ""                # the human grouping — one walk's worth of related checks
section: ""             # legacy "1.3"-style number, kept for addressing continuity
ordinal: 0              # display order within the area; sparse, so an insert shifts nothing
mark: " "               # THE VERDICT: " " | x | / | - | ! | ?   (TAXONOMY.md, "`mark` (checks)")
verdict_date: ""        # when the current mark was recorded
verdict_reason: ""      # required for / - ! ?
invalidated_by: {}      # {change: TASK-0000, reason: "", date: ""} — TESTING.md rule 3, as a field
automation: manual      # full | partial | manual
covered_by: []          # the TST-* notes or modules providing that coverage
covers: []              # what this check verifies — [[FEAT-...]], [[ISS-...]]
burden: []              # what a walker must have to hand
evidence: []            # paths, screenshots, log excerpts behind the current verdict
migrated_from: ""       # pre-migration address + sha, for suites that came from ACCEPTANCE_TESTS.md
related: []
---

# <Check>

<One sentence: what a person does, and what they should see. This is the line that used to be the checkbox — keep it that short.>

## Procedure

- <the steps, if the sentence above is not enough>

## Expected

- <what "passed" means, precisely enough that two people would agree>

## Verdict history

<The current verdict lives in `mark:` / `verdict_date:` / `verdict_reason:`. The full history is `git log -L` on this file — do not maintain a second copy of it here.>
