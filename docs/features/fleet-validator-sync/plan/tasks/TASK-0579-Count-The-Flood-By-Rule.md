---
type: "[[task]]"
id: TASK-0579
aliases: ["TASK-0579"]
title: "Count the flood by rule — run the upstream validator against all four fleet repos in report-only mode and record what it actually reports"
status: done
phase: "[[PHASE-041-The-Gate-Runs-Where-The-Checks-Are]]"
owner: user:edwin
created: 2026-08-29
updated: 2026-08-29
source: ["[[ISS-0209-The-Acceptance-Gate-Reaches-No-Fleet-Repo]]"]
parent: "FEAT-0143"
effort: ""
due: ""
depends: []
blocks: ["TASK-0580"]
related: []
tests: []
---

# Count the flood by rule

## Definition of Done
- [x] Upstream's `validate-docs.py --repo-root <repo>` is run against all four fleet repos and the errors are counted **by rule**.
- [x] Each fleet validator's divergence is measured twice — against upstream HEAD, and against the repo's own recorded sync baseline — because the two numbers answer different questions.
- [x] Each repo's post-baseline additions are checked for presence in upstream HEAD, so `--force` can be justified rather than assumed.
- [x] The result is written into `plan/PLAN.md`, [[PHASE-041-The-Gate-Runs-Where-The-Checks-Are]] and [[ISS-0209-The-Acceptance-Gate-Reaches-No-Fleet-Repo]].

## Notes

[[ISS-0209]] records that copying upstream's validator into `your-sudoku` produced *"a flood"* — and nobody counted it. An uncounted flood is what made this look like four unbounded reconciliations.
