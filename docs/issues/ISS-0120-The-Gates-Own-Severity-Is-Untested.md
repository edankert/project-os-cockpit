---
type: "[[issue]]"
id: ISS-0120
aliases: ["ISS-0120"]
title: "A gate demoted from error to warning leaves every test green, so nothing guards the severity that makes a gate a gate"
status: "fixed"
phase: ""
owner: user:edwin
created: 2026-08-06
updated: "2026-08-13"
source: ["review:independent"]
severity: medium
component: "validator"
parent: ""
related: ["[[FEAT-0081-What-A-Session-Costs-To-Keep-Alive]]", "[[TASK-0356-The-Snapshot-Membership-Gate]]"]
tests: []
---

# A gate demoted from error to warning leaves every test green

## Problem

Found by round 4 of the independent review of [[FEAT-0081]], by mutation rather than by reading.

Replacing `emit_for("SNAPSHOT-MEMBERSHIP", ...)` with `report.warn` leaves all eleven cases in `tests/test_parent_backlink.py` passing. The same holds for `PARENT-BACKLINK`. Both suites assert the code appears in the validator's output; neither asserts it appears as an **error**.

Severity is the whole point of a gate. A check that warns is a check the pre-commit hook and CI both ignore, so the demotion that silently disables it is exactly the edit no test would catch — and "the test passes" would remain true throughout.

This is a repo-wide pattern rather than something either gate introduced. The asserts are shaped `assert "CODE" in out`, and `out` contains both tiers.

## Repro

```
sed -i '' 's/emit = emit_for("SNAPSHOT-MEMBERSHIP", feat_id)/emit = report.warn/' tools/scripts/validate-docs.py
.venv/bin/pytest tests/test_parent_backlink.py -q     # 11 passed
```

## Expected

A gate's tests assert the tier: `ERROR [CODE]` for an ungrandfathered violation, `WARN` for a grandfathered one. `tests/test_parent_backlink.py` already distinguishes the two in `test_the_real_repo_has_no_new_backlink_errors`, so the shape exists — it is simply not used in the synthetic cases.

## Actual

Every synthetic case matches the bare code, so error and warning are indistinguishable to the suite.

## Scope

Deliberately filed rather than fixed with [[FEAT-0081]]. It is not a defect of that feature — it is a property of how gate tests are written across this repo, and the fix should be applied to all of them at once by someone looking at the whole set, not bolted onto a feature about prompt-cache economics.

## Next Actions

- [ ] Assert the tier in the synthetic cases for `PARENT-BACKLINK` and `SNAPSHOT-MEMBERSHIP`
- [ ] Sweep the other gate suites for the same shape
- [ ] Consider a helper that asserts `ERROR [CODE]` / `WARN [CODE]` so the bare-code form is hard to write by accident

## Fixed — 2026-08-13

Every synthetic case in `tests/test_parent_backlink.py` now asserts the **tier** through `_assert_error` / `_assert_absent` rather than the bare code, and the helper carries the reason so the next gate's tests inherit the shape instead of reinventing `assert "CODE" in out`.

**Verified with this issue's own repro.** Demoting `SNAPSHOT-MEMBERSHIP` to `report.warn` used to leave 11 passing; it now fails 2. Demoting `PARENT-BACKLINK` fails 3. `validate-docs.py` is unchanged — it is template-owned, and only the mutation was applied and reverted.
