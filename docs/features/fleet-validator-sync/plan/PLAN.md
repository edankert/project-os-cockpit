# Plan — the fleet runs one validator

[[PHASE-041-The-Gate-Runs-Where-The-Checks-Are]], [[ISS-0209-The-Acceptance-Gate-Reaches-No-Fleet-Repo]]. One feature, eight tasks, two tests.

## The census came first, and it changed the plan

[[PHASE-041]]'s step 0 was *"count the flood before choosing anything"*, on the grounds that it *"may well show the reconciliation is two or three mechanical rules, which would change everything below."* It did.

| repo | notes | own validator | upstream validator | PARENT-BACKLINK | SNAPSHOT-MEMBERSHIP | other |
|---|---|---|---|---|---|---|
| `obsidian-supernote-sync` | 88 | 0 errors | **16** | 12 | 4 | 0 |
| `your-health` | 782 | 0 errors | **271** | 257 | 14 | 0 |
| `your-sudoku` | 604 | 0 errors | **194** | 186 | 8 | 0 |
| `your-trainer` | 2519 | 0 errors | **605** | 589 | 16 | 0 |
| | | | **1086** | **1044** | **42** | **0** |

**Two rules, 100% of the errors, and they are one relationship.** `PARENT-BACKLINK` fires when `TASK-X` declares `parent: FEAT-Y` and `FEAT-Y` does not name it in `tasks:`. `SNAPSHOT-MEMBERSHIP` fires when the snapshot's `tasks:` list for a feature disagrees with the note's. Writing each feature's `tasks:` to the set of tasks that declare it as parent, then running `sync-snapshot.py`, answers both.

## The second finding is what makes the sync possible at all

`sync-project-os.sh --dry-run` reports `validate-docs.py` as **DIVERGED** in every fleet repo and refuses to touch it, which is the mechanism that kept the fleet behind while routine syncs reported success. But the divergence it is detecting is **21–100 lines against each repo's own recorded baseline**, not the ~780 against upstream HEAD — that larger number is upstream having moved, which is staleness rather than local work.

And the local work is not local. Diffing each fleet validator's post-baseline additions against upstream HEAD:

| repo | lines added since baseline | not present in upstream HEAD |
|---|---|---|
| `obsidian-supernote-sync` | 23 | **0** |
| `your-health` | 16 | 4 (comment wording only) |
| `your-sudoku` | 79 | 32 (ADR-0030's retired `CHK`/`checks` collection) |
| `your-trainer` | 79 | 32 (same) |

Every hand-applied change is either already upstream or is [[ADR-0030]] support that [[ADR-0031]] **retired** by folding `check` into `test` at `level: acceptance` — which upstream carries and the fleet does not. So `--force` loses nothing, and the census run proves it: upstream's validator executed against these corpora reports those two rules and nothing else.

## Order

1. **[[TASK-0579]] — the census.** Done first, recorded, because the estimate it replaces is what parked this in `PHASE-999` for a quarter.
2. **[[TASK-0580]] — the tool.** `migrate-fleet-validator.py`: force-sync the template files, reconcile the backlinks, re-run. Guarded by [[TST-0080]] before it touches a repo.
3. **[[TASK-0581]]–[[TASK-0584]] — the four migrations, cost-ascending.** `obsidian-supernote-sync` (16 errors) is the rehearsal that proves the route at 3% of the hard repo's size; `your-trainer` (605) is attempted last.
4. **[[TASK-0585]] — the drift check**, with [[TST-0081]]. In the goal rather than a follow-up because the measured drift is ~93 lines per eleven days: a one-shot catch-up regresses.
5. **[[TASK-0586]] — `your-trainer` scopes `REL-0013` from its note**, which is the exit criterion that turns the migration into the thing [[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]] decided.

## What the census also corrected

`VERIFY-ACCEPTANCE` is a **warning** upstream, inside a grandfather window ending **2026-11-20**, and it fires **10** times against `your-sudoku` — `FEAT-0025` against `TST-0028..0033` and `FEAT-0028` against `TST-0018..0021`. [[ISS-0209]] describes *"six true `VERIFY-ACCEPTANCE` findings"* that *"fire in no pre-commit and in no CI"*. Six is `FEAT-0025`'s share; the other four were not counted. And after the migration they will still not block — they warn until November, then become errors. Installing the gate and having it *gate* are two dates, and the issue's "done when" reads as one.

## What the plan did not contain, added at close

**A report-only census counts the rules that can fire against the corpus *as it stands*, and fixing rule A can arm rule B.** `your-trainer`'s reconciliation produced 15 `VERIFY` errors that the census had reported **zero** of — because `VERIFY` reads a feature's `tasks:` from the **snapshot**, and with those lists absent it had nothing to walk. Filling them in was the migration's entire content. The census's *"nothing else at all"* was a true measurement and was never a prediction, and no amount of care in running it would have shown this. Recorded in `your-trainer`'s `tools/GRANDFATHERED.yaml` (155 → 158) rather than guessed at: either those tasks finished and were never closed, or three features are not done, and marking 15 tasks `done` on the balance of probability writes a guess into the record.

**`your-trainer`'s snapshot writes each feature as a one-line flow mapping** — `FEAT-0020: { file: "...", status: backlog }` — which the tool's block-form reader matched none of. Its first real run there reported *"0 snapshot entries"* and left all 33 `SNAPSHOT-MEMBERSHIP` errors standing: a migration reporting success against work it had not done, in the largest repo in the fleet. Guarded now by `test_a_one_line_flow_mapping_in_the_snapshot_is_reconciled`.

**The drift check gates on rule codes, not lines.** Written as a line threshold first, which fails `project-os-cockpit` — 1105 lines from upstream and *ahead* of it, because new rules are authored here. Missing **rule codes** separates behind from ahead exactly: 0 for the four migrated repos and the cockpit, 10 for the six that hold no acceptance checks.

**Nine mutants, one survivor.** Deleting the writer's byte-identity early return passed all fifteen tests, because `plan_backlinks` short-circuits before reaching it and a satisfied feature never enters `plan.additions`. The guard was real and nothing exercised it; four tests now drive `set_frontmatter_list` directly. A tenth mutant — putting the drift check's summary line back on stdout under `--json` — was found by piping the tool's own output into `json.load`.

**The validator cannot see a note whose frontmatter is not YAML**, and that hid a defect written during this work through two green pre-commit runs in `your-trainer`. [[ISS-0260-Unparseable-Frontmatter-Is-Validated-Against-A-Different-Note]].
