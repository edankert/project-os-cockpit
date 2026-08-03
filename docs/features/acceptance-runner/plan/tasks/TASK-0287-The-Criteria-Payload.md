---
type: "[[task]]"
id: TASK-0287
aliases: ["TASK-0287"]
title: "The criteria payload — a feature's requirements' criteria with their resolved states, from the parse the validator already trusts"
status: backlog
phase: "[[PHASE-024-Acceptance-Witnessed]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[FEAT-0063-The-Acceptance-Runner]]"]
parent: "[[FEAT-0063-The-Acceptance-Runner]]"
effort: M
depends: []
blocks: []
related: []
tests: []
---

# The criteria payload

## Definition of Done

- `GET /api/notes/acceptance?id=FEAT-…` returns each requirement's criteria with state (open / ticked / reconciled), witness and evidence where present.
- The parse is shared with or fixture-proven identical to REQ-BOXES — a criterion the validator counts is a criterion the runner walks, always.
- A feature with no criteria returns the nothing-to-accept answer, which FEAT-0065 counts as debt.
