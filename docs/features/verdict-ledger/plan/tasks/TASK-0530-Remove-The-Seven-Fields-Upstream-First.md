---
type: "[[task]]"
id: TASK-0530
aliases: ["TASK-0530"]
title: "Remove the seven verdict fields from the schema, the template and the validator — upstream first"
status: done
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

- [x] `SCHEMAS.md` "Acceptance fields" describes only intent: `tier`, `area`, `section`, `ordinal`, `covers`, `burden`, `migrated_from`, `merged_from`.
- [x] `docs/__templates__/test.md` scaffolds none of the seven.
- [x] `TESTING.md` and `STATUSES.md` describe the ledger rather than `mark:`.
- [x] The validator errors on any of the seven, and the message names the ledger — for `evidence` it names the ledger's `evidence` collection specifically ([[TASK-0544]]), because a message that just says *"the ledger"* leaves a person hunting for a field that is not there.
- [x] `tests_verified:` leaves the **release** template and schema in the same pass ([[TASK-0546]]) — it is the same decision one level up, and splitting it across two syncs means two rounds of fleet divergence.
- [x] **All of it lands in `~/Dev/repos/project-os` first** ([[ADR-0030]] decision 6), then `sync-project-os.sh` down.

## Notes

`covers:` stays. It is intent and it is the gating axis ([[ADR-0034]] d1, [[ADR-0032]]).

`tier:` stays here. [[ISS-0208]] owns it and is orthogonal — where a verdict is stored says nothing about which checks gate.

**Do not sync down into `your-trainer` or `your-sudoku` without reading [[ISS-0217]] first.** Both repos' `TESTING.md` and `SCHEMAS.md` are a schema generation behind — they still describe the retired `[[check]]` type — and `your-trainer`'s tier definitions in `TESTING.md` are its own content, cited by [[DES-0012]] D3. A blind copy would delete them.

## Done 2026-08-19 — upstream first, and the removal is CONDITIONAL

`~/Dev/repos/project-os@ce789d7` carries `SCHEMAS.md`, `TAXONOMY.md` and `test.md`; the same edits are here.

**Targeted edits, not a file copy — and that is a finding.** The two repos' copies of these files diverge **in both directions**: upstream has `origin:`, the rule-ADR body sections and `deferred:` that this repo lacks; this repo has `aliases:`, `platform:`, `tags:` and `deciders:` that upstream lacks. A sync in either direction would have destroyed work. [[ISS-0217]] names this hazard for the fleet repos; it is true of this pair too, and nothing reports it.

**The validator refuses the seven fields ONLY in a repo that keeps ledgers** (`LEDGER-FIELD`). Eight of twelve fleet repos have no ledger, and a schema change that broke every repo which had not migrated would be a worse failure than the one it fixes. Same discriminator that keeps `mark_check` alive, and the same reason.

`automation` also leaves `TAXONOMY.md` — [[DES-0012]] D2 already made `command:` the single answer to *who runs this*.
