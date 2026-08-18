---
type: "[[task]]"
id: TASK-0476
aliases: ["TASK-0476"]
title: "The validator learns the merged type — status tables, collections, metrics, and the badge guard"
status: backlog
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
source: ["[[FEAT-0118-The-Test-Type-Absorbs-The-Check]]"]
parent: "[[FEAT-0118-The-Test-Type-Absorbs-The-Check]]"
effort: M
depends: ["[[TASK-0475-Level-Acceptance-Becomes-The-Discriminator]]"]
blocks: []
related: []
tests: []
---

# The validator learns the merged type

`tools/scripts/validate-docs.py` and its bundled mirror `validate_docs_bundled.py`: `ALLOWED_STATUS`, `COLLECTION_TYPE` (the `checks` collection retires), `METRIC_PREFIX_TYPE` (the `CHK` row goes with the prefix). The two copies must not drift — the bundled one exists so the cockpit can validate without the repo's scripts, and the parity guard already covers it.

**And the guard [[REQ-0037-The-Badge-Never-Admits-Acceptance-Tests]] asks for lands here**, before any migration runs: an assertion that no note at `level: acceptance` is ever counted by the Run obligation, at any status. It must fail loudly rather than warn — 669 rows arriving on a badge is not a warning-shaped event.

Done when: both validators accept the merged type, reject an acceptance test at a status the Run obligation counts, and the fleet still validates green.
