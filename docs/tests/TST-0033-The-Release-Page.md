---
type: "[[test]]"
id: TST-0033
aliases: ["TST-0033"]
title: "The release page — its payload, its refusals, and the absence of `window.prompt`"
status: passing
covers: ["[[FEAT-0106-The-Release-Page]]"]
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["[[FEAT-0106]] acceptance criteria"]
scope: system
level: integration
entrypoint: ""
command: ".venv/bin/pytest tests/test_release_page.py -q"
last_verified: ""
issues: ["[[ISS-0176-Every-Prompt-In-The-Desktop-Shell-Is-Dead]]"]
tasks: ["[[TASK-0440-The-Release-Payload]]", "[[TASK-0441-The-Release-Page-And-An-Input-That-Works]]"]
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

# The release page

## Purpose

The payload and the refusals, plus the one assertion that would have caught [[ISS-0176]] two features ago: **`window.prompt` appears nowhere in the renderer.**

Every dead control had tests on its payload, its write path and its endpoint. None pressed the button. That is the link no test touched and the only one a person uses.

## Procedure

Run the command; the file's docstrings carry each case.
