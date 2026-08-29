---
type: "[[test]]"
id: TST-0081
aliases: ["TST-0081"]
title: "The drift check fails when the fleet falls behind — the failing branch is exercised, and a missing validator is not silently a divergence of zero"
status: active
covers: ["[[TASK-0585]]"]
owner: user:edwin
created: 2026-08-29
updated: 2026-08-29
phase: "[[PHASE-041-The-Gate-Runs-Where-The-Checks-Are]]"
source: ["[[ISS-0209-The-Acceptance-Gate-Reaches-No-Fleet-Repo]]"]
scope: system
level: unit
entrypoint: ""
command: ".venv/bin/pytest tests/test_fleet_drift.py -q"
last_verified: ""
issues: ["[[ISS-0209]]"]
tasks: ["[[TASK-0585]]"]
artifacts: []
related: ["[[FEAT-0143]]"]
---

# The drift check fails when the fleet falls behind

Automated, in `tests/test_fleet_drift.py`.

## What it pins

**That it fails.** A guard whose failing branch has never been seen is an assumption. The test constructs a repo whose validator diverges past the threshold and requires a non-zero exit; it also constructs one at exactly the threshold and requires zero, because an off-by-one on a threshold turns a guard into noise or into nothing.

**That absence is not agreement.** A repo with no `tools/scripts/validate-docs.py` must be reported as *absent*, and a missing or unreadable upstream must be reported as *cannot compare* — two outcomes, neither of them "0 lines diverged, all good". This is the failure this whole phase is about: a check that reports success because it could not look.

**That the gate is counted, not inferred.** `_acceptance_is_settled` occurring zero times is the finding [[ISS-0209]] opens with. The check reports the count per repo, and the test pins that a validator without it is reported as gateless even when its line divergence is small.

## Why a threshold rather than exact equality

Because `merge`-owned files and per-repo `STATUSES.md` overrides mean a fleet repo is legitimately allowed to differ, and a check that demands byte equality would be turned off within a week. The threshold's value and its reason are recorded next to it; the test pins the boundary behaviour, not the number.
