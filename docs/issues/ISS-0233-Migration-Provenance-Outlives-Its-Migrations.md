---
type: "[[issue]]"
id: ISS-0233
aliases: ["ISS-0233"]
title: "`migrated_from`, `merged_from`, the `CHK-*` alias and `burden` are carried on every check and none of them is information the record plans to keep"
status: fixed
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
severity: medium
component: acceptance
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[ISS-0224-The-Positional-Address-Outlived-The-Document]]", "[[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]]", "[[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]]"]
---

# Provenance of migrations that are over

Edwin, 2026-08-19: *"remove ordinal and section and migrated from — this is not information we plan to carry forward. (review other properties that we do not intend to carry forward as well)"*

[[ISS-0224]] took `section` and `ordinal`. The census of what is left says the same thing about three more.

| field | non-empty | what it is |
| --- | --- | --- |
| `migrated_from` | **34 of 34** | the address in `ACCEPTANCE_TESTS.md` plus the sha, from [[ADR-0030]] |
| `merged_from` | **34 of 34** | the `CHK-*` id and sha, from [[ADR-0031]] |
| `aliases: [… "CHK-0001"]` | **34 of 34** | the retired id, kept so a `[[CHK-*]]` link would resolve |
| `burden` | **0 of 34** | what a walker must have to hand — designed for, never used |

**All three of the first are provenance of migrations that are finished**, and each was justified at the time by the same sentence: blame does not survive the rewrite, so the record carries it instead. That was true while the migration was recent and somebody might need to trace a note back. Two migrations later it is a permanent field on every check describing a document nobody can open, in a repo where the id has not changed since.

**Git holds it.** The migration commits are in history with their shas, and [[ADR-0030]] and [[ADR-0031]] both name theirs. A field is the wrong place for a fact that is already immutable somewhere better.

**The `CHK-*` alias was kept for inbound links, and [[ADR-0031]] measured that there are none** — *"zero inbound `[[CHK-*]]` references exist anywhere in the fleet."* It has been resolving nothing for a day.

**`burden` is empty everywhere.** Edwin: *"drop burden."*

## Suggested fix

Remove all four from `test.md`, `SCHEMAS.md` and the validator — **upstream first, so they cannot come back on the next sync** — and strip them from `project-os-cockpit`, `your-trainer` and `your-sudoku`.

The validator refuses them **only in a repo that keeps ledgers**, the same conditional [[ADR-0037]] used, so a repo that has not migrated is untouched.

## Done when

- [x] The four fields are gone from all three suites and from the upstream template.
- [x] The validator refuses them where a ledger exists.
- [x] No inbound `[[CHK-*]]` link exists — re-measured, not assumed.

## Fixed 2026-08-19
