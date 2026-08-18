---
type: "[[test]]"
id: TST-0066
aliases: ["TST-0066", "CHK-0023"]
title: "The validator's answer is on screen"
status: active
owner: user:edwin
created: 2026-08-17
updated: 2026-08-17
tier: 1
area: "Verification health and the fleet"
section: "1.11"
ordinal: 10
mark: "x"
verdict_date: ""
verdict_reason: ""
invalidated_by: {}
automation: manual
covered_by: []
covers: ["[[FEAT-0018]]", "[[FEAT-0028]]"]
burden: []
evidence: []
migrated_from: "tests/ACCEPTANCE_TESTS.md#1.11.1 @ 7de1a86"
related: []
level: acceptance
kind: manual
merged_from: "CHK-0023 @ 4c02731"
---

# The validator's answer is on screen

expect the health surface to agree with `bash tools/scripts/validate-docs.sh` run in a terminal — same error count, same notes named. — 2026-08-11, **rendered**, and this check went `[x]` → `[ ]` → `[x]` in one day, which is the record working. *First pass compared a clean repo — `validator clean` against `0` errors. Agreement, about nothing, and the second clause recorded as vacuous. Driven against a clone carrying four deliberate errors, the count still matched exactly and **the surface named none of them**, so the tick was withdrawn.* **Now fixed and re-walked.** Terminal: `ITEM-STATUS TST-0011`, `COUNTER ISS-9101`, `COUNTER ISS-9102`, `METRICS metrics.counts.issues_triage is 10 but computed 12` — four. Screen, in the same card: `validator: 4 errors` over four rows — `TST-0011 · status drift: snapshot=passing note=failing`, `ISS-9101 · exceeds counters.ISS`, `ISS-9102 · exceeds counters.ISS`, and the metrics line, which carries no id and correctly shows only its message. **Same count, same notes named**, both clauses met against real errors rather than against zero. The payload had carried `id`/`rel`/`url` per error since [[FEAT-0018]]; only the card had never read them. (user:edwin, 2026-08-11)
