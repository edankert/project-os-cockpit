---
type: "[[task]]"
id: TASK-0480
aliases: ["TASK-0480"]
title: "The fleet: `your-sudoku` (56), then `your-trainer` (579) last"
status: backlog
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
source: ["[[FEAT-0119-The-Merge-Migration]]"]
parent: "[[FEAT-0119-The-Merge-Migration]]"
effort: L
depends: ["[[TASK-0479-Pilot-This-Repo]]"]
blocks: []
related: []
tests: []
---

# The fleet migration

`your-sudoku` second — 56 checks, all blocking, a real gate under load and a repo whose surfaces this session has not shaped. Then `your-trainer` last: 579 checks, 60 blocking, twelve historical tags, and the two-shape delta that `suite_at` reads at every one of them.

**`suite_at`'s two-shape branch becomes three shapes and must not.** It reads file shape before the document cut and note shape after; a merged note is still note shape, so the branch is untouched **provided the reader keys on `level: acceptance` rather than on the id prefix**. Assert the delta at all twelve `your-trainer` tags before and after — the figures are 1, 10, 10, 15, 26, 85, 130, 22, 47, 47, 47, 47, and they are the one thing this migration could silently break.

**The frozen per-release suites do not move** ([[ADR-0030]] decision 5, carried forward): `ACCEPTANCE_TESTS_v2.1.0.md` and its siblings are records of what past releases were measured against.

Done when: all three repos migrated, every parity assertion green per repo, the twelve-tag delta unchanged, and no repo's Tests badge has moved.


## Blocked — and by what, precisely

**Not started, and the reason is a sequencing constraint the plan named and under-costed.** [[ADR-0030]] decision 6, carried into [[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]], says template-owned surfaces land upstream before any note changes downstream. Measured today: **every repo's copy of `validate-docs.py` and its four instruction files are locally diverged**, so `sync-project-os.sh` correctly refuses to overwrite them — the same guard that protected this repo.

`your-sudoku` was taken as far as the sync and then **returned to exactly the state it was found in** (`git status` clean, untracked leftovers removed). A three-way patch cannot be applied there: the base blobs live in the `project-os` object store, not in `your-sudoku`'s, so `git apply -3` has nothing to merge against. Each repo needs a hand-merge of its own divergence, which is a per-repo exercise and not a fleet loop.

**What that means for the phase:** the merged type, the automation path and the link normalisation are implemented, tested and demonstrable **in this repo**, on its 34 real acceptance notes. `your-sudoku` (56) and `your-trainer` (579) still hold `CHK-*` notes and still read correctly, because `acceptance.load` reads both shapes and `covers_index` falls back to the forward field names — a repo that has not migrated loses nothing.

**Do not force it.** `--force` on a diverged template file discards downstream content the report explicitly warns about, and `your-trainer` is already failing validation with 600 errors from causes that predate this work. Migrating 579 notes into a repo whose validator does not know the merged type would add its errors to that pile and make both harder to read.

## Next actions

- [ ] Hand-merge the template divergence in `your-sudoku`, then migrate its 56 and assert parity.
- [ ] Same for `your-trainer`, and assert the twelve-tag delta (1, 10, 10, 15, 26, 85, 130, 22, 47, 47, 47, 47) before and after — the one thing this migration could silently break.
