---
type: "[[task]]"
id: TASK-0480
aliases: ["TASK-0480"]
title: "The fleet: `your-sudoku` (56), then `your-trainer` (579) last"
status: backlog
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
source: ["[[FEAT-0119-The-Merge-Migration]]"]
parent: "[[FEAT-0119-The-Merge-Migration]]"
effort: L
depends: ["[[TASK-0479-Pilot-This-Repo]]"]
blocks: []
related: []
tests: []
---

# The fleet migration

`your-sudoku` second — 56 checks, all blocking, a real gate under load and a repo whose surfaces this session has not shaped. Then `your-trainer` last: 579 checks, 60 blocking, twelve historical tags, and the two-shape delta that `suite_at` reads at every one of them.

**`suite_at`'s two-shape branch becomes three shapes and must not.** It reads file shape before the document cut and note shape after; a merged note is still note shape, so the branch is untouched **provided the reader keys on `level: acceptance` rather than on the id prefix**. Assert the delta at all twelve `your-trainer` tags before and after — the figures are 1, 10, 10, 15, 26, 85, 130, 22, 47, 47, 47, 47, and they are the one thing this migration could silently break.

**The frozen per-release suites do not move** ([[ADR-0030]] decision 5, carried forward): `ACCEPTANCE_TESTS_v2.1.0.md` and its siblings are records of what past releases were measured against.

Done when: all three repos migrated, every parity assertion green per repo, the twelve-tag delta unchanged, and no repo's Tests badge has moved.
