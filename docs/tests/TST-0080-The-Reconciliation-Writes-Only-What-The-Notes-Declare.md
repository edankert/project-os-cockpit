---
type: "[[test]]"
id: TST-0080
aliases: ["TST-0080"]
title: "The backlink reconciliation writes only what the notes declare — it is idempotent, it never invents membership, and removal is reported before it happens"
status: active
covers: ["[[TASK-0580]]"]
owner: user:edwin
created: 2026-08-29
updated: 2026-08-29
reviewed_by: model:claude-opus-5
review_date: 2026-08-29
review_verdict: changes-requested
review_response: "All nine findings acted on; the verdict stands as written. CODE (1-5): the add-only merge loop, the partly-populated-list path and `main()` itself all now have tests -- `main()` was reached by nothing, so the dry-run snapshot preview AND ISS-0257's artefact pruning were both unguarded. `RULE_RE` gained a `\\b`, because `emit` was matching as a SUBSTRING inside `promotion_emit(` and three of the four call names in the alternation were doing nothing; the fixture now carries a wrapped call and a `report,`-prefixed one, so both sub-patterns are load-bearing. The writer balances brackets (a flow list closing at column 0 left an orphan `]` and produced unparseable frontmatter -- ISS-0260 reintroduced by the tool that found it) and reads CRLF and a BOM; `apply_plan` reports an unreadable note instead of raising, because it writes file by file AFTER the forced validator copy. NUMBERS (6): all four reproduce the reviewer's way -- your-sudoku 57 not 59, your-trainer 625 not 628, the fleet 682/716 not 669, and 784 is a raw diff where the label said whitespace-normalised (776). Corrected in PHASE-041, TASK-0583, TASK-0584, ISS-0209 and the CHG, with the propagation path named. GOAL (7): PHASE-041 now says in its own body that nothing runs the drift check, so the goal sentence is not met even though criterion 4 literally is. LEDGER (8): your-trainer ISS-0378 files the fifteen VERIFY findings, and the ledger entry now records both irregularities -- that the file says it only shrinks, and that `cutover:` frames these as promotion-time debt when they were invisible rather than exempted. WORDING (9): the BACK_FIELDS comment no longer claims to mirror an order it deliberately reverses, and TASK-0580's box no longer describes a removal the tool does not do. Ten mutants re-run, every one now fails a named test; 42 tests, suite green, validator 0 errors."
review_response_date: 2026-08-29
phase: "[[PHASE-041-The-Gate-Runs-Where-The-Checks-Are]]"
source: ["[[ISS-0209-The-Acceptance-Gate-Reaches-No-Fleet-Repo]]"]
scope: system
level: unit
entrypoint: ""
command: ".venv/bin/pytest tests/test_fleet_migration.py -q"
last_verified: ""
issues: ["[[ISS-0209]]"]
tasks: ["[[TASK-0580]]"]
artifacts: []
related: ["[[FEAT-0143]]"]
---

# The reconciliation writes only what the notes declare

Automated, in `tests/test_fleet_migration.py`.

## What it pins

**That the direction is note → feature, and only that direction.** `PARENT-BACKLINK` and `SNAPSHOT-MEMBERSHIP` are one relationship seen from two ends, and [[ADR-0009]] settles which end authors it: the note. The reconciliation reads every task's `parent:` and writes the feature's `tasks:`. A test asserts the reverse never happens — a `tasks:` entry that no task claims is **reported**, never quietly kept and never quietly dropped.

**That a second run is a no-op.** The tool has to be safe to run on a repo somebody already ran it on, because that is what the fifth repo will look like. Idempotence is asserted by running it twice against the same fixture and requiring the second run to report zero writes and leave the bytes identical.

**That a dangling parent is not membership.** A task declaring `parent: FEAT-9999` where no such feature exists must not create an entry, must not crash, and must appear in the report. This is the case where "fix the errors" and "make the validator quiet" come apart.

**That the frontmatter survives the rewrite.** The corpus being edited is 3993 notes across four repos, hand-written over months. A YAML round-trip that reorders keys, drops comments, or reflows a hard-wrapped string is a silent 3993-file diff wearing a one-line change's clothes. The test asserts that reconciling a note whose `tasks:` is already correct changes **no bytes at all**, which is the only formulation that catches a reformatter.

## What it does not pin

It does not assert that the migration makes any particular repo green — that is each migration task's own definition of done, verified by running the validator there. This module tests the operation, on fixtures it owns.


## Independent review — 2026-08-29, `model:claude-opus-5`, `changes-requested`

Fresh context, separate session from the author's; same model family, recorded in `reviewed_by:` as provenance (ADR-0013). Twenty-nine independently constructed mutants were run against `tools/scripts/migrate-fleet-validator.py` on top of the nine the work reports. Fifteen were killed. The survivors that matter are all in this note's own claims:

- **"never quietly dropped" is unguarded.** Deleting the merge loop in `plan_backlinks` that carries forward `tasks:`/`issues:` entries no child claims passes all 19 tests. Five live entries in the fleet would be silently deleted by the mutant on their next rewrite.
- **The partial-list case has no fixture.** Every test starts from a feature whose list is empty, complete, or satisfied via `fixes:`. Changing `set(children) <= named_anywhere` to `set(children) & named_anywhere` — skip a feature once *any* one child is named — passes all 19.
- **`main()` is never invoked.** `test_dry_run_reports_the_same_writes_and_makes_none` calls `reconcile_snapshot` with `planned_tasks` directly, so the wiring in `main()` that supplies it survives being replaced by `None` — the exact "preview silent about half the work" failure the function's docstring names. `prune_artefacts`, `parse_synced_paths`, `superset_report` and `run_sync` are likewise unexercised.
- **The `FEAT`-only guard on `parent:` is untested** and is load-bearing on the real corpus: 19 tasks across three fleet repos declare an `ISS-*` parent. Without it the tool writes `tasks:` into issue notes.
- **Hostile note shapes are not covered.** A top-level flow list with its closing `]` at column 0 produces unparseable frontmatter — the very defect ISS-0260 was opened for; CRLF and BOM notes raise `ValueError` out of `apply_plan`, which has no error handling and writes note-by-note, so a crash leaves a half-migrated corpus after `--force` has already replaced the validator. Three flow-spanning and two CRLF notes exist in the fleet today.

Also killed and worth recording as genuinely guarded: byte-identity, idempotence, the `fixes:`-satisfies rule, the flow-mapping snapshot reader, the block-sequence depth read, dangling parents, and `planned_tasks`. Idempotence was additionally confirmed end-to-end against all four real corpora (0 rewrites, 0 snapshot changes).
