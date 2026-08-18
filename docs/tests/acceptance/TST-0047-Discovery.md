---
type: "[[test]]"
id: TST-0047
aliases: ["TST-0047", "CHK-0004"]
title: "Discovery"
status: active
owner: user:edwin
created: 2026-08-17
updated: 2026-08-17
tier: 1
area: "Desktop shell and workspaces"
section: "1.2"
ordinal: 10
mark: done
verdict_date: ""
verdict_reason: ""
invalidated_by: {}
automation: manual
covered_by: []
covers: ["[[FEAT-0007]]", "[[FEAT-0009]]", "[[FEAT-0016]]"]
burden: []
evidence: []
migrated_from: "tests/ACCEPTANCE_TESTS.md#1.2.1 @ 7de1a86"
related: []
level: acceptance
merged_from: "CHK-0004 @ 4c02731"
---

# Discovery

launch the shell with no arguments. Expect: every `SNAPSHOT.yaml`-bearing repo under `~/Dev/repos/` appears in the rail, each with its own sidecar. — 2026-08-10, live shell over CDP: **10** rail squares, each carrying its validator verdict and remote state (`no remote — nothing is backed up` on `articles`; `34 commits not pushed (remote is a deploy target)` on `your-applications.com`).
