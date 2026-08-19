---
type: "[[test]]"
id: TST-0034
aliases: ["TST-0034"]
title: "A release shows the record it kept — what it verified, what it shipped with, what it published, and never today's gate"
status: active
covers: ["[[FEAT-0107-Publication-Is-A-List-Of-Releases]]"]
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["[[FEAT-0107]] acceptance criteria"]
scope: system
level: integration
entrypoint: ""
command: ".venv/bin/pytest tests/test_release_record.py -q"
last_verified: ""
issues: []
tasks: ["[[TASK-0443-Releases-Are-The-Navigator]]", "[[TASK-0444-A-Shipped-Release-Shows-Its-Own-Record]]", "[[TASK-0445-Capture-At-Ship]]"]
artifacts: []
evidence: []
adequacy: ""
mutation_score: ""
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[ADR-0028-Work-Has-Three-Phases]]"]
---

# A release shows the record it kept

## Purpose

The finding [[FEAT-0107]] turned on: **Edwin's model was already implemented, in his files, and nothing read it.** `tests_verified:`, the known-issues section and the platform artifacts have been maintained by hand across twelve releases and were invisible.

So most of these assert *reading*, not new behaviour. The last one checks the claim against the real corpus rather than a fixture, because "the record is already there" is a statement about `your-trainer` and not about a temp directory.

## Procedure

Run the command; the file's docstrings carry each case.
