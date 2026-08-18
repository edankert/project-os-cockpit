---
type: "[[task]]"
id: TASK-0474
aliases: ["TASK-0474"]
title: "The test schema absorbs the check's fields, and `check.md` is deleted"
status: backlog
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
source: ["[[FEAT-0118-The-Test-Type-Absorbs-The-Check]]"]
parent: "[[FEAT-0118-The-Test-Type-Absorbs-The-Check]]"
effort: M
depends: ["[[TASK-0473-Test-Statuses-Gain-Active-And-Retired]]"]
blocks: []
related: []
tests: []
---

# The test schema absorbs the check fields

`test.md` gains `mark`, `tier`, `area`, `section`, `ordinal`, `verdict_date`, `verdict_reason`, `invalidated_by`, `automation`, `covered_by`, `burden`, `migrated_from` and `merged_from` — all optional, all meaningful only at `level: acceptance`. SCHEMAS.md documents which fields apply at which level, because a schema that lists twenty fields with no rule about when they apply is a schema nobody can satisfy.

`check.md` is **deleted, not tombstoned**: the template directory is a scaffolding source, and a template for a type the validator rejects scaffolds broken notes. Same reasoning [[ADR-0030]] decision 4 used for `ACCEPTANCE_TESTS.md`.

Done when: a note scaffolded from `test.md` at `level: acceptance` validates, `check.md` is gone upstream and here, and no template references the check type.
