---
type: "[[test]]"
id: TST-0050
aliases: ["TST-0050", "CHK-0007"]
title: "Nothing is unreachable"
status: active
owner: user:edwin
created: 2026-08-17
updated: 2026-08-17
tier: 1
area: "The navigator"
section: "1.3"
ordinal: 20
mark: "x"
verdict_date: ""
verdict_reason: ""
invalidated_by: {}
automation: manual
covered_by: []
covers: ["[[FEAT-0010]]", "[[FEAT-0046]]", "[[FEAT-0058]]", "[[FEAT-0085]]"]
burden: []
evidence: []
migrated_from: "tests/ACCEPTANCE_TESTS.md#1.3.2 @ 7de1a86"
related: []
level: acceptance
kind: manual
merged_from: "CHK-0007 @ 4c02731"
---

# Nothing is unreachable

pick a task, a plan and a requirement at random from `docs/` and find each in the tree. Expect: all three, without using the find bar. — 2026-08-11, **rendered**, sampled by stride from `ls` rather than chosen: **TASK-0160** (`account-budget`), **`docs/features/agent-activity/plan/PLAN.md`**, **REQ-0007**. All three reached by expanding only — PHASE-007 → FEAT-0035 → PLAN → TASK-0160; PHASE-007 → FEAT-0020 → PLAN (opened, `docs/features/agent-activity/plan/PLAN.md` in the centre pane); PHASE-001 → FEAT-0001 → REQ-0007. **FEAT-0035 sits behind the fold**, not missing: PHASE-007 has 20 features against `NAV_GROUP_FOLD_LIMIT = 12`, and the `… 8 more` control reveals exactly the eight the DOM was holding back. Fold on volume, never on meaning — the check would have failed if the eight had no way in. (user:edwin, 2026-08-11)
