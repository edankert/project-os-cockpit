---
type: "[[task]]"
id: TASK-0486
aliases: ["TASK-0486"]
title: "Backfill `covers:` on the ten tests that resolve only by path or by a feature's edge"
status: done
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

## Done

`covers:` populated on **all 43 tests** in this repo — the union of the `features:`/`verifies:`/`validates:`/`requirements:` they already carried, plus the three that resolved only by path (TST-0017 → FEAT-0027, TST-0018 → FEAT-0036, TST-0019 → FEAT-0006).

**The eight unreciprocated edges were read, not guessed, and seven resolved in the FEATURE's favour** — which is the opposite of what the "the many side is right" argument predicted, and is recorded because it complicates it:

| edge | resolution |
|---|---|
| FEAT-0023/0024/0025/0026/0027 → TST-0011 | **the features were right.** TST-0011's checklist items cite them by number in its body (*"9. Overview scopes (FEAT-0023)"*, *"11. Dispatch runtime (FEAT-0025/0026)"*). Its frontmatter named four features; it covers **nine**. |
| FEAT-0057/0058 → TST-0023 | **the features were right.** The test asserts phase-group banding and the fold invariant, which is FEAT-0057's record grammar and FEAT-0058's navigator shape as much as FEAT-0056's ordering. |
| FEAT-0117 → TST-0043 | **the test was right.** TST-0043 pins Mark-released's two refusals, the frozen feature list, that it runs no git, and that a prose `tests_verified` reads as a claim. None of that is *one view per item*. FEAT-0117's claim was unfounded and is dropped rather than carried across. |

**The other seven of the ten backfills are in `your-health` (5) and `project-os-dev` (2) and are NOT done here.** Those repos are 13–18 upstream commits behind and their validators do not yet read `covers:`; consolidating their fields before they sync would move data into a field nothing there reads. They are covered by the forward-field fallback in `covers_index` instead, so they lose nothing in the meantime. Owed on their next template sync.

**The 25 genuinely system-wide tests keep an empty `covers:`, deliberately** — [[REQ-0040-One-Verification-Link]] says so, and a backfill that guessed an owner would replace an honest absence with a plausible wrong answer.
