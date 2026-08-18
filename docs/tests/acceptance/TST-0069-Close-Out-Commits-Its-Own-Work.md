---
type: "[[test]]"
id: TST-0069
aliases: ["TST-0069", "CHK-0026"]
title: "Close-out commits its own work"
status: active
owner: user:edwin
created: 2026-08-17
updated: 2026-08-17
tier: 1
area: "Close-out"
section: "1.13"
ordinal: 10
mark: done
verdict_date: ""
verdict_reason: ""
invalidated_by: {}
automation: manual
covered_by: []
covers: ["[[FEAT-0055]]"]
burden: []
evidence: []
migrated_from: "tests/ACCEPTANCE_TESTS.md#1.13.1 @ 7de1a86"
related: []
level: acceptance
merged_from: "CHK-0026 @ 4c02731"
---

# Close-out commits its own work

run `tools/scripts/close-out-commit.sh <paths…>`. Expect: named paths staged, dirty files elsewhere reported and left alone, the message built from the staged ids, the pre-commit hook run, and no push. — 2026-08-10: exercised **13 times** across this release; messages built from staged ids (`FEAT-0090 TASK-0377 TASK-0378 TST-0022: …`), the validator ran at pre-commit each time, and one invocation correctly **refused** `desktop/dist` as gitignored rather than committing it. Nothing pushed.
