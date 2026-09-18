---
type: "[[change]]"
id: CHG-20260918-The-Cockpit-Runs-The-Templates-Validator
title: "The cockpit runs the template's validator again"
status: merged
owner: user:edwin
created: 2026-09-18
updated: 2026-09-18
source: ["[[project-os-dev#ISS-0068]]", "Edwin, 2026-09-18: 'Do ISS-0068 now'"]
commit: ""
pr: ""
impacts: []
issues: []
features: []
reviewed_by: ""
review_date: ""
review_verdict: ""
related: []
---

# The cockpit runs the template's validator again

## Summary

This repository's `tools/scripts/validate-docs.py` and its bundled copy in `src/` are the template's again, and the `keep_local:` line that held them back is gone. Until today the cockpit carried its own validator, with rules the rest of the fleet never got, while the template gained rules the cockpit never got.

The cockpit's own rules were moved into the template first (project-os-dev ISS-0068): STATUS-VALUE-NOTE, CHECK-SUBJECT, SURFACE-ORPHAN, REVIEW-STALE, RELEASE-PREPARING, and the check that an automated test's command still names something that exists (now its own code, VERIFY-COMMAND). What the cockpit gains from the template includes the acceptance gate reading the release ledger, which clears 42 of this repo's 61 VERIFY-ACCEPTANCE warnings.

## What changed for this repository

- **Two rules have a new name.** TEST-AUTOMATED-STATUS and TEST-AUTOMATED-EVIDENCE were this repository's form of the template's COMMAND-VERDICT, the same rule written twice. `tests/test_automated_test_holds_no_verdict.py` now names COMMAND-VERDICT; every case in its matrix gives the same answer as before.
- **Dates are the fleet's.** COMMAND-VERDICT becomes an error on 2026-12-02; CHECK-SUBJECT, SURFACE-ORPHAN, REVIEW-STALE, STATUS-VALUE-NOTE and VERIFY-COMMAND on 2026-12-17. The ledger checks LEDGER-FIELD, LEDGER-SEALED and NOTE-FRONTMATTER warn until 2026-12-17 instead of erroring at once; this repository has none of them.
- **The command check is faster.** `command_targets.py` and the validator skip `.git`, build output, dependency folders and Python environments when looking for a test file. On your-health the validator took 197 s with the search as it was and 12 s with this.
- **`generate-adapters.py` is the template's**, so this repository now carries the Codex skills and subagents under `.agents/` and `.codex/`, as every other fleet repo does.
- **The walk files are the template's** (project-os c71dbb7), which already held everything this repository's copies had.

Two defects in the template were found by this repository's tests on the way and fixed there: the sealed-ledger check used `hashlib` without importing it, and an acceptance check with a command at `ready` was reported twice.

## Verification

- `python -m pytest tests` in a clean worktree at HEAD with this change: 2,146 passed, 10 failed, 16 skipped. The same 10 fail at HEAD without it (`test_fleet_validate` three, `test_surface_type` two, `test_guided_walk_ledger_copy` two, `test_completed_work_ordering`, `test_cross_repo_links`, `test_digest_watermark`), so none is caused by this change. Before the retargeting, 14 more failed; all are accounted for above.
- The merged validator was run over all 13 fleet repositories: no repository gains an error.

## Impact

- No screen changed. The validator report the shell shows (`shell.validation`) lists different rules, as described above; the capability itself is unchanged, so the register is not edited.
