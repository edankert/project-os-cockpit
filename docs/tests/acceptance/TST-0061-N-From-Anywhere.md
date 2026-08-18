---
type: "[[test]]"
id: TST-0061
aliases: ["TST-0061", "CHK-0018"]
title: "⌘N from anywhere"
status: active
owner: user:edwin
created: 2026-08-17
updated: 2026-08-17
tier: 1
area: "Issues and capture"
section: "1.8"
ordinal: 10
mark: "x"
verdict_date: ""
verdict_reason: ""
invalidated_by: {}
automation: manual
covered_by: []
covers: ["[[FEAT-0061]]"]
burden: []
evidence: []
migrated_from: "tests/ACCEPTANCE_TESTS.md#1.8.1 @ 7de1a86"
related: []
level: acceptance
kind: manual
merged_from: "CHK-0018 @ 4c02731"
---

# ⌘N from anywhere

press ⌘N on any note, type a sentence, Enter. Expect: an `ISS-*` at `triage`, linked to the note you were on, appearing in the triage tray without a reload. — 2026-08-11, **rendered**, against an isolated clone of this repo so the probe writes never touch the record: on `docs/README.md`, ⌘N opened `CAPTURE AN ISSUE · LINKED TO DOCS-README` (*Enter files it at triage · Esc closes*); Enter answered `ISS-0137 captured at triage` and the context pane gained `ISSUES 1 · triage` **without a reload**. On disk: `status: triage`, `related: ["[[DOCS-README]]"]` — linked to the note I was on, not to the workspace. (user:edwin, 2026-08-11)
