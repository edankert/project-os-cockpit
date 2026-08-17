---
type: "[[task]]"
id: TASK-0461
aliases: ["TASK-0461"]
title: "Pilot on this repo — 34 rows, the everything-green corpus, where a wrong mark is visible immediately"
status: done
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
source: ["[[FEAT-0113-The-Check-Type-And-The-Migration]]"]
parent: "[[FEAT-0113-The-Check-Type-And-The-Migration]]"
effort: S
depends: ["[[TASK-0460-The-Migration-Script]]"]
blocks: []
related: ["[[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]]"]
tests: []
---

# Pilot this repo

This repo migrates first: 34 rows, all settled, the tool's own corpus — a wrong mark or a lost row is visible immediately and costs nothing downstream. `your-sudoku` and `your-trainer` wait for [[TASK-0463-The-Fleet-Migrates-Trainer-Last]], after the schema has survived a real sweep here.

## Done when

- [ ] 34 `CHK-*` notes exist, the validator is green, and `gate_payload` reports the same counts (34 settled, 0 blocking) from notes as it did from the file.
- [ ] The release page and the Tests view render against the migrated corpus with no dead rows and no missing groups.
- [ ] The suite's own acceptance walk — this repo's checks — can be performed against the new storage.
