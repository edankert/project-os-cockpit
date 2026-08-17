---
type: "[[task]]"
id: TASK-0460
aliases: ["TASK-0460"]
title: "The migration script — parse, emit one CHK note per row, delete the source, assert parity rather than assuming it"
status: backlog
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
source: ["[[FEAT-0113-The-Check-Type-And-The-Migration]]"]
parent: "[[FEAT-0113-The-Check-Type-And-The-Migration]]"
effort: M
depends: ["[[TASK-0459-The-Check-Type-Lands-Upstream]]"]
blocks: []
related: ["[[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]]"]
tests: []
---

# The migration script

`acceptance.parse` already yields every field — tier, section, area, ordinal, mark, refs, rerun, text — so the script is parse → write N notes under `docs/tests/acceptance/` → delete `docs/tests/ACCEPTANCE_TESTS.md` → one commit. Deleted, not tombstoned: a left-behind file is the dual-source trap this project has paid for twice, and git holds it at every pre-migration ref. A short README says where checks live and how to read pre-migration history.

Each note carries `migrated_from:` — the old `#section.ordinal` address plus the pre-migration sha — because blame will not cross the cut (~2% similarity; rename detection will not fire) and traceability is preserved by the record rather than the plumbing. The old `number` stays as an alias so existing links resolve. The `CHK` counter is created and `sync-snapshot.py` raises it like any other.

## Done when

- [ ] The script asserts, per run: row count in = notes out; every mark, tier, rerun reason and ref byte-equal through a parse-back — ISS-0175's lesson, applied in advance.
- [ ] The frozen per-release snapshot suites are untouched, by construction — the script reads exactly one path.
