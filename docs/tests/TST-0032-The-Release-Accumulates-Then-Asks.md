---
type: "[[test]]"
id: TST-0032
aliases: ["TST-0032"]
title: "The release accumulates, then asks — open is silent, preparing gates, and shipping freezes what it named"
status: passing
covers: ["[[FEAT-0105-There-Is-Always-A-Release]]"]
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["FEAT-0105-There-Is-Always-A-Release acceptance criteria"]
scope: system
kind: automated
level: integration
entrypoint: ""
command: ".venv/bin/pytest tests/test_release_lifecycle.py -q"
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

# TST-0032

## Purpose

See [[FEAT-0105-There-Is-Always-A-Release]]. The assertions are its acceptance criteria, and the ones that matter most are the states that are *incomplete rather than wrong* — those fail nothing on their own and show up only as a record nobody can act on.

## Procedure

Run the command. The file's docstrings carry what each case pins and why.
