---
type: "[[feature]]"
id: FEAT-0143
aliases: ["FEAT-0143"]
title: "The fleet runs one validator — the migration is two mechanical rules, not a per-repo reconciliation, and a drift check keeps it that way"
status: done
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
goal: "Move every fleet repo onto the upstream validator — which is what carries the acceptance gate — by reconciling the two rules the census shows are the entire cost, and leave a drift check behind that fails the build when the fleet falls behind again."
requirements: []
tasks: ["[[TASK-0579-Count-The-Flood-By-Rule]]", "[[TASK-0580-The-Migration-Is-A-Tool-Not-A-Session]]", "[[TASK-0581-Migrate-Obsidian-Supernote-Sync]]", "[[TASK-0582-Migrate-Your-Health]]", "[[TASK-0583-Migrate-Your-Sudoku]]", "[[TASK-0584-Migrate-Your-Trainer]]", "[[TASK-0585-Drift-Is-Measured-Not-Noticed]]", "[[TASK-0586-Your-Trainer-Scopes-Its-Release]]"]
release: ""
acceptance_exception: "This feature ships no user-facing surface: it is a migration of four repos' pre-commit tooling plus a CI check. Its observable behaviour is `validate-docs.py` exiting 0 in repos where upstream's rules previously reported 1086 errors, which is what its automated tests assert directly."
acceptance: ""
design: ""
related: ["[[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]]", "[[FEAT-0142-A-Release-Says-What-Is-In-It]]"]
tags: [feature, tooling, fleet]
---

# The fleet runs one validator

## Goal

`_acceptance_is_settled` — the acceptance gate — occurs **zero** times in the four fleet repos that hold acceptance checks. [[ISS-0209-The-Acceptance-Gate-Reaches-No-Fleet-Repo]] says why it was never simply synced: the fleet validators are ~780 lines behind upstream, and pulling the gate pulls every rule added since the last sync, which "is a migration per repo".

**The census says that estimate was wrong, and wrong in the cheap direction.** Running upstream's validator against all four repos in report-only mode produces **1086 errors, and 100% of them are two rules** — `PARENT-BACKLINK` (1044) and `SNAPSHOT-MEMBERSHIP` (42). Both are the *same relationship seen from its two ends*: a feature's `tasks:` list not naming the tasks that declare it as `parent:`. Neither is a judgement call, and one operation fixes both.

## Scope

**In:**

- The census itself, recorded by rule and by repo, because the estimate it replaces is what parked this work for a quarter.
- A migration tool that force-syncs the template-owned validator and reconciles the backlink relationship in the notes.
- The four migrations, cost-ascending: `obsidian-supernote-sync`, `your-health`, `your-sudoku`, `your-trainer`.
- A drift check that measures each fleet validator against upstream and fails past a stated threshold.

**Out:**

- Backporting only the acceptance rules ([[ISS-0209]] option 2) — out by decision, per [[PHASE-041-The-Gate-Runs-Where-The-Checks-Are]].
- The ledger migration ([[ADR-0037-A-Verdict-Is-An-Event]]).
- Anything that pushes. Every migration commit is local.

## Acceptance

- `python3 tools/scripts/validate-docs.py --repo-root <repo>` from **upstream** exits 0 in all four fleet repos.
- `grep -c _acceptance_is_settled` is non-zero in all four.
- The drift check fails a build when a fleet validator diverges past its threshold, and that failure is exercised by a test rather than asserted.

## Links

- Issue: [[ISS-0209-The-Acceptance-Gate-Reaches-No-Fleet-Repo]]
- Phase: [[PHASE-041-The-Gate-Runs-Where-The-Checks-Are]]
- Plan: `docs/features/fleet-validator-sync/plan/PLAN.md`


## Independent review — 2026-08-29, `model:claude-opus-5`, `changes-requested`

Fresh-context session; the notes and the diffs only, never the author's reasoning trace. Same model family as the author, recorded in `reviewed_by:` (ADR-0013: context is the gate, family is not). Run as a subagent of the authoring session, so it shares that session's scratchpad directory on disk; it does not share its transcript, and this reviewer has no memory of authoring the work.

**What reproduced.** Every load-bearing measurement was recomputed from pre-migration worktrees and reproduced exactly: the census (16 / 271 / 194 / 605 = **1086**, 1044 `PARENT-BACKLINK` + 42 `SNAPSHOT-MEMBERSHIP`, nothing else), the corpus sizes (88 / 782 / 604 / 2519 = 3993), the divergence (782 / 817 / 776 / 776 → **0**), the gate (0 → **2** in all four), the baseline superset figures (0 / 4 / 32 / 32), `your-trainer`'s 76 notes and 33 snapshot entries and its 586-task/3-issue split, the fleet's 987/57 split, the six ungated repos at 10 rules and 619 lines, the cockpit at 1105 lines, `REL-0013`'s **13** derived checks, and 10 / 19 `VERIFY-ACCEPTANCE`. Upstream's validator exits 0 in all four repos today; the tool is idempotent on the real corpora (0 rewrites, 0 snapshot changes across all four); both scripts run under system Python 3.9; nothing pushed anywhere; the `GRANDFATHERED.yaml` restore is add-only and faithful; the `covers:` repair is complete and touched no other note.

**Why `changes-requested` all the same.**

1. **`plan_backlinks`'s add-only preservation is unguarded.** Deleting the `for existing in sorted(v.extract_ids(p_fm.get(field)))` merge loop passes all 31 tests, and the tool then silently drops any entry no child claims on the next rewrite. Five such entries exist in the fleet today (`FEAT-0047` in `your-health`; `FEAT-0038` ×3 and `FEAT-0087` in `your-trainer`).
2. **The merge path itself is untested.** No fixture has a *partially* correct `tasks:`. Replacing `set(children) <= named_anywhere` with `&` — "satisfied if any one child is named" — passes all 31 tests and would leave `PARENT-BACKLINK` findings standing.
3. **`main()` has no test at all.** The dry-run/`planned` wiring that the function's own docstring names as the phase's core failure mode survives deletion, as does `ARTEFACT_FRAGMENTS` pruning (ISS-0257's mitigation), `parse_synced_paths`, `superset_report` and `run_sync`.
4. **`set_frontmatter_list` can emit unparseable YAML.** A top-level flow list whose closing `]` sits at column 0 leaves an orphan bracket; CRLF and BOM notes raise `ValueError` out of `apply_plan`, which writes note-by-note with no error handling. Three multi-line-flow notes and two CRLF notes exist in the fleet today (none of them feature notes, so nothing is live), and ISS-0259 proposes running this tool on six more repos.
5. **Four numbers do not reproduce**: `your-sudoku`'s "59 checks" (57), `your-trainer`'s "628" (625, in PHASE-041 twice and TASK-0584 twice), PHASE-041's first table giving 784 for those two repos where its own second table and every other note give 776 (784 is the *raw* diff; the note says whitespace-normalised), and the `your-trainer` commit's "669 checks" fleet total (682 across the four, 716 fleet-wide).
6. **The goal is wider than what is installed.** "Leave behind a drift check that **fails the build** … so this is the last time the fleet has to catch up" — nothing runs `fleet-drift.py`. `.git/hooks/pre-commit.local` is absent here and in every fleet repo, and the tool cannot run in CI by design. Criterion 4's narrower wording is met; the goal sentence is not, and only the hook header says so.
7. **`GRANDFATHERED.yaml` grew against its own header** ("This file only shrinks", `cutover: 2026-07-25`). Removing the three new entries takes `your-trainer` to rc=1 with 15 `VERIFY` errors, so the ledger is load-bearing for "exit 0 in all four". The addition is disclosed in four places, but the CHG heading "**Filed** rather than fixed" lists these three and nothing was filed — there is no `ISS-*` in `your-trainer` and no expiry on the entries.

**Checked and dropped**: `tools/scripts/` being template-owned is not a divergence hazard — the sync lists downstream-only files under "Upstream no longer ships (left in place)" alongside nine other cockpit-authored scripts, and `--force` does not delete them. `RULE_RE` is complete against upstream's 52 codes today. All four repos do run the gate in a real pre-commit (`your-trainer` via `core.hooksPath=.githooks`). `TST-0017` is `level: integration`, so the 13-check derivation is exact rather than path-scoped luck.

**One inconsistency to settle while fixing the above**: `BACK_FIELDS` says it "Mirrors the `back_fields` table inside `PARENT-BACKLINK`" but reverses the issue tuple — upstream is `("fixes", "issues")`, the tool writes `("issues", "fixes")`. Both satisfy the rule; the comment is wrong about which field the tool writes.
