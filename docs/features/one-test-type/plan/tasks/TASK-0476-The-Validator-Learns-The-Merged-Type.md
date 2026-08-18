---
type: "[[task]]"
id: TASK-0476
aliases: ["TASK-0476"]
title: "The validator learns the merged type — status tables, collections, metrics, and the badge guard"
status: done
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

## Done

Both validators know the merged type. **`ACCEPTANCE-STATUS` is a new ERROR**: an acceptance test holding `ready`/`passing`/`failing` *without* a `command:` fails the build, because that is ADR-0031's central construction failing silently. `command:` is the deliberate exception — a test that declares how to run itself has been automated, and the runner owns it from then on.

**The validator's own guard caught the first cut**: `ACCEPTANCE_FORBIDDEN_STATUSES` was flagged by the unregistered-status-collection rule (the ISS-0012/ISS-0013 guard), so it is registered in `FLAT_STATUS_TABLES` against the `test` type rather than exempted — a typo in it would otherwise disarm the assertion silently.

**And the bundled copy is a verbatim bundle, not a fork** — hand-mirroring the change failed `test_bundled_validator_matches_the_canonical_one` immediately, which is the guard doing exactly its job.
