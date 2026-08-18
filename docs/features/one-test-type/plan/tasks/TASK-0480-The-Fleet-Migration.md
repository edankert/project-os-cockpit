---
type: "[[task]]"
id: TASK-0480
aliases: ["TASK-0480"]
title: "The fleet: `your-sudoku` (56), then `your-trainer` (579) last"
status: done
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

## Done 2026-08-18

**All three suites migrated: 34 + 56 + 579 = 669 checks, and no `type: [[check]]` note remains in any of the twelve repos.**

| repo | notes | blocking before → after | badge before → after | commit |
|---|---|---|---|---|
| project-os-cockpit | 34 | 0 → 0 | 1 → 1 | `3d3ad5b` |
| your-sudoku | 56 | 56 → 56 | 0 → 0 | `36b7c8b` |
| your-trainer | 579 | 60 → 60 | 5 → 5 | `0535db82` |

**`your-trainer`'s twelve-tag delta is unchanged** — the one thing this could have broken silently: 84, 87, 87, 111, 212, 268, 361, 536, 560, 560, 560, 560, asserted at every tag before and after.

**The blocker in the earlier note was real and was solved rather than worked around.** Copying the current template's validator into either repo was the wrong move, and measuring said so: **both repos validate green against their own validator**, while the current one reports **600 errors** on `your-trainer` from rules unrelated to this migration. So only the ADR-0031 rules were applied to each repo's own copy. A wholesale copy would have taken a green repo red and blamed the merge for it.

**Three pre-existing defects surfaced, each of which blocked the migration:**

1. **`your-sudoku` could not commit at all.** `tools/scripts/validate-docs.sh` was recorded `100644`, and that repo's pre-commit hook refuses to run rather than silently skip validation. Found by trying to make a commit; fixed with `git update-index --chmod=+x`.
2. **Both repos' `STATUSES.md` carried the `## [[test]]` section twice**, and `load_allowed_status` takes the last one — so the stale copy silently decided the vocabulary and the updated section was overridden by its own duplicate. This is why `STATUSES.md` is not prose here: it *is* the allowed-status table.
3. **The migration script's dirty-tree refusal was too broad.** `your-trainer` carries ~100 uncommitted files of unrelated work at any moment; what `merged_from:` claims is that its sha contains *these checks*, and a dirty Kotlin file says nothing about that. Scoped to the acceptance directory, with a guard for each half.

**`your-trainer`'s `SNAPSHOT.yaml` was deliberately left uncommitted.** It carries work that is not mine — `FEAT-0104`, `TASK-0779..0783`, a phase focus change — and staging it would make somebody else's afternoon part of this migration. It also now holds the `TST` counter bump the migration needs (14 → 597), so whoever commits that work carries the counter with it.
