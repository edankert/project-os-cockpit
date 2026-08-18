---
type: "[[task]]"
id: TASK-0486
aliases: ["TASK-0486"]
title: "Backfill `covers:` on the ten tests that resolve only by path or by a feature's edge"
status: backlog
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
source: ["[[FEAT-0121-The-Verification-Link-Normalises]]"]
parent: "[[FEAT-0121-The-Verification-Link-Normalises]]"
effort: S
depends: []
blocks: []
related: []
tests: []
---

# Backfill `covers:` on the ten

Of the 35 tests declaring no feature: **3** resolve by path only, **7** by the feature's `tests:` edge, **25** by neither. The ten get an explicit `covers:`; the 25 stay empty **deliberately** and that is stated in [[REQ-0040-One-Verification-Link]] — they are system-wide, and guessing an owner replaces an honest absence with a plausible wrong answer.

**The 20 unreciprocated edges are resolved in the same pass.** Each is a feature claiming a test verifies it where the test does not agree; each needs a person to say which side was right, and doing it here means the disagreement is settled while both sides still exist to compare. Afterwards there is only one side ([[ISS-0199-Twenty-Of-Sixty-One-Feature-To-Test-Edges-Are-Not-Reciprocated]]).

Done when: ten notes carry `covers:`, twenty disagreements are resolved with the winning side recorded, and the 25 system-wide tests are listed in the task's close-out as deliberately unowned.
