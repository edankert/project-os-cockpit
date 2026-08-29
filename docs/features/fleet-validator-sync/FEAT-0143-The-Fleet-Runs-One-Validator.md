---
type: "[[feature]]"
id: FEAT-0143
aliases: ["FEAT-0143"]
title: "The fleet runs one validator — the migration is two mechanical rules, not a per-repo reconciliation, and a drift check keeps it that way"
status: done
owner: user:edwin
created: 2026-08-29
updated: 2026-08-29
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
