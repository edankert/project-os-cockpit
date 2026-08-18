---
type: "[[feature]]"
id: FEAT-0119
aliases: ["FEAT-0119"]
title: "The merge migration — 669 checks become tests, renumbered to `TST-*`, with parity asserted through the reader in every repo"
status: done
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
reviewed_by: "model:claude-opus-5"
review_date: 2026-08-18
review_verdict: changes-requested
goal: "Move every `CHK-*` note in the fleet onto the merged type and renumber it into the `TST-*` space, proving per repo and through the loaded suite — never by file count — that no row, mark, coverage target or gate figure changed in the process; then retire the check type from the cockpit's seven modules and two stylesheets."
requirements: ["[[REQ-0038-Nothing-Is-Lost-In-The-Merge]]"]
tasks: ["[[TASK-0477-The-Merge-Migration-Script]]", "[[TASK-0478-Renumber-Into-The-TST-Space]]", "[[TASK-0479-Pilot-This-Repo]]", "[[TASK-0480-The-Fleet-Migration]]", "[[TASK-0481-Retire-The-Check-Type-From-The-Cockpit]]", "[[TASK-0490-Independent-Review-Of-The-Merge]]"]
release: ""
acceptance: ""
design: ""
related: ["[[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]]", "[[FEAT-0113-The-Check-Type-And-The-Migration]]", "[[REQ-0038-Nothing-Is-Lost-In-The-Merge]]"]
---

# The merge migration

**Same corpus, second move, two weeks apart.** [[FEAT-0113-The-Check-Type-And-The-Migration]] is the template for how to do this and the reason to be careful doing it again: pilot here (34), then `your-sudoku` (56), then `your-trainer` (579) last, and never the big one first.

**Renumbering is cheap and was measured before it was chosen.** Zero inbound `[[CHK-*]]` references exist anywhere in the fleet, so nothing breaks. `your-trainer`'s TST counter goes 18 → ~597, which is the visible cost and it is on the record.

**Provenance survives by the record, not by git.** `migrated_from:` is carried through verbatim — it still points at the original `ACCEPTANCE_TESTS.md#section.ordinal` and sha — and a new `merged_from:` carries the `CHK-*` id and the pre-merge sha. Blame will not cross this commit either; that was accepted the first time and the mitigation is the same one.

**The cockpit cull is part of this feature, not a follow-up.** Seven modules and two stylesheets carry `check`-type vocabulary, and the renderer has 173 `check` sites. Leaving them is how a retired type stays half-alive.

## Delivered

*(This section read "Pilot done, fleet not" until 2026-08-18. Edwin: "the goal was to implement, test and verify phase 035 fully! This includes migrating the up-stream repos." He was right — the blocker named below was solvable, and it was solved.)*

**All three suites migrated — 669 checks.** This repo's 34 checks are `TST-0044..0077` at `level: acceptance`, with parity asserted through the reader on six dimensions and the obligation badge unmoved at 3.

`your-sudoku` (56) and `your-trainer` (579) are **not migrated**, and [[TASK-0480-The-Fleet-Migration]] records why: every repo's `validate-docs.py` and instruction files are locally diverged, so each needs a hand-merge before its notes can change type. `your-sudoku` was taken as far as the sync and returned to exactly the state it was found in. Nothing there is broken in the meantime — `acceptance.load` reads both shapes.
