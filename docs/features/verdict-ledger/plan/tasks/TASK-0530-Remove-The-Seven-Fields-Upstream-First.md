---
type: "[[task]]"
id: TASK-0530
aliases: ["TASK-0530"]
title: "Remove the seven verdict fields from the schema, the template and the validator — upstream first"
status: backlog
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
parent: "[[FEAT-0134-The-Note-Sheds-The-Verdict]]"
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
tags: [task]
---

# Seven fields leave

`mark`, `verdict_date`, `verdict_reason`, `invalidated_by`, `automation`, `covered_by`, `evidence`.

## Definition of Done

- [ ] `SCHEMAS.md` "Acceptance fields" describes only intent: `tier`, `area`, `section`, `ordinal`, `covers`, `burden`, `migrated_from`, `merged_from`.
- [ ] `docs/__templates__/test.md` scaffolds none of the seven.
- [ ] `TESTING.md` and `STATUSES.md` describe the ledger rather than `mark:`.
- [ ] The validator errors on any of the seven, and the message names the ledger.
- [ ] **All of it lands in `~/Dev/repos/project-os` first** ([[ADR-0030]] decision 6), then `sync-project-os.sh` down.

## Notes

`covers:` stays. It is intent and it is the gating axis ([[ADR-0034]] d1, [[ADR-0032]]).

`tier:` stays here. [[ISS-0208]] owns it and is orthogonal — where a verdict is stored says nothing about which checks gate.

**Do not sync down into `your-trainer` or `your-sudoku` without reading [[ISS-0217]] first.** Both repos' `TESTING.md` and `SCHEMAS.md` are a schema generation behind — they still describe the retired `[[check]]` type — and `your-trainer`'s tier definitions in `TESTING.md` are its own content, cited by [[DES-0012]] D3. A blind copy would delete them.
