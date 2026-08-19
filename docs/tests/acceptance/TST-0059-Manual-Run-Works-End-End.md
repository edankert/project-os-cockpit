---
type: "[[test]]"
id: TST-0059
aliases: ["TST-0059", "CHK-0016"]
title: "A manual run works end to end"
status: active
owner: user:edwin
created: 2026-08-17
updated: 2026-08-17
tier: 1
area: "Tests"
section: "1.7"
ordinal: 20
covers: ["[[FEAT-0086]]"]
burden: []
migrated_from: "tests/ACCEPTANCE_TESTS.md#1.7.2 @ 7de1a86"
related: []
level: acceptance
merged_from: "CHK-0016 @ 4c02731"
---

# A manual run works end to end

open a manual test, press `Run ▸`, walk the steps with evidence, record. Expect: the note gains `status`, `last_run` and a `## Runs` entry, and nothing else changes. — 2026-08-11, **rendered**, isolated clone, [[TST-0011]] (this repo's only `kind: manual` test): `VERIFY · Run · 13 steps` opens the runner at `~tests/TST-0011/run`, one step at a time with `Pass` / `Fail` / `Skip` and an evidence field. Recorded, the diff is **exactly** `status: passing → failing`, `last_run: → 2026-08-11`, `updated:`, and an appended `### 2026-08-11 — failing (by user:edwin)` block with a line per step. **`last_verified` correctly did not move** — a failing run makes no claim to have verified anything. **The run's subject was not exercised** (its steps need a live agent session), so what is walked here is the runner, and every step carries a verdict that says so. (user:edwin, 2026-08-11)
