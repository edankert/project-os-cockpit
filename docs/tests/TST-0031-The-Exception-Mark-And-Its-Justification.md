---
type: "[[test]]"
id: TST-0031
aliases: ["TST-0031"]
title: "The exception mark and its justification — the cycle writes on every click, an unjustified exception is owed, and clicking past it leaves nothing behind"
status: passing
covers: ["[[FEAT-0104-The-Suite-Is-The-Surface]]"]
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["FEAT-0104-The-Suite-Is-The-Surface acceptance criteria"]
scope: system
level: integration
entrypoint: ""
command: ".venv/bin/pytest tests/test_acceptance_exceptions.py -q"
last_verified: ""
issues: []
tasks: []
artifacts: []
evidence: []
last_run: "2026-08-16T00:00Z"
exit_code: 0
adequacy: ""
mutation_score: ""
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[ADR-0028-Work-Has-Three-Phases]]"]
---

# TST-0031

## Purpose

See [[FEAT-0104-The-Suite-Is-The-Surface]]. The assertions are its acceptance criteria, and the ones that matter most are the states that are *incomplete rather than wrong* — those fail nothing on their own and show up only as a record nobody can act on.

## Procedure

Run the command. The file's docstrings carry what each case pins and why.
