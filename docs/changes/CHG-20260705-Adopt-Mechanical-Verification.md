---
type: "[[change]]"
id: CHG-20260705-Adopt-Mechanical-Verification
aliases: ["CHG-20260705-Adopt-Mechanical-Verification"]
title: "Adopt project-os mechanical verification (validator, blocking hooks, pre-commit/CI) and fix snapshot drift it caught"
status: merged
owner: user:edwin
created: 2026-07-05
updated: 2026-07-05
source:
  - ../project-os/docs/changes/CHG-20260705-Mechanical-verification-and-independent-review.md
commit: ""
pr: ""
impacts:
  - "tools/scripts"
  - "tools/adapters/claude-code"
  - "tools/skills"
  - "tools/instructions"
  - "docs/__templates__"
  - ".github/workflows"
  - ".claude/settings.json"
  - "SNAPSHOT.yaml"
issues: []
features: ["[[FEAT-0018-Verification-Health-Surface]]"]
related:
  - tools/scripts/validate-docs.py
---

# Adopt Mechanical Verification

## Summary
Targeted sync of the upstream project-os enforcement change set: docs validator (`tools/scripts/validate-docs.py`), blocking PreToolUse verification gate, Stop-hook validation, git pre-commit hook (installed), CI workflow, and the new `independent-review` and `docs-audit` skills. A full `sync-project-os.sh` run was deliberately avoided because this repo carries local content in nominally template-owned paths (`docs/PHASES.md`, `docs/phases/`, `docs/__templates__/SCHEMAS.md`); those files were merged by hand instead.

## Impact
- `.claude/settings.json` now enables the project-os hook set, including the blocking verification gate (deny on terminal status without passing linked tests; `verification_waiver` is the recorded escape).
- `git commit` now runs the docs validator via pre-commit; `.github/workflows/validate-docs.yml` is the CI backstop.
- `LIFECYCLE.md` merged: spec-ambiguity check at classify, validator + independent-review steps at close-out, cockpit-focus steps preserved.
- `SCHEMAS.md` merged: adequacy/mutation/review fields added to test and change schemas alongside this repo's local `aliases`/`platform`/`tags` extensions.
- **Drift fixed (found by the validator's first run):** TASK-0048..TASK-0052 had no note path in SNAPSHOT.yaml; PHASE-003/PHASE-004 used `backlog` (not in the phase taxonomy — now `planned`, aligned in snapshot, phase notes, and PHASES.md); `counters.WF` was 0 with WF-0001..0003 present (now 3).
- Known deviation, accepted for now: this snapshot uses `path:` where SNAPSHOT.md specifies `file:`; the validator accepts the alias and emits a single warning. Migration can happen in a dedicated pass.

## Documentation Coverage (All Types Considered)
Set each item to one of: `updated`, `new`, `not-applicable`, `deferred`.

- features: new
- requirements: not-applicable
- tasks: new
- issues: not-applicable
- tests: not-applicable
- workflows: not-applicable
- decisions: not-applicable
- risks: deferred
- changes: new
- snapshot: updated

## Follow-ups
- [ ] Implement [[FEAT-0018-Verification-Health-Surface]] (validation endpoint, health badge + drift panel, waiver/review/adequacy badges).
- [ ] Migrate snapshot `path:` keys to `file:` per SNAPSHOT.md in a dedicated commit.
- [ ] Consider a `RISK-*` for the python3 runtime requirement of the hooks (likely subsumed by existing [[RISK-0003-Python-Runtime-Floor]]).
