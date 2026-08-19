---
type: "[[test]]"
id: TST-0048
aliases: ["TST-0048", "CHK-0005"]
title: "Switching"
status: active
owner: user:edwin
created: 2026-08-17
updated: 2026-08-17
tier: 1
area: "Desktop shell and workspaces"
section: "1.2"
ordinal: 20
covers: ["[[FEAT-0007]]", "[[FEAT-0009]]", "[[FEAT-0016]]"]
burden: []
migrated_from: "tests/ACCEPTANCE_TESTS.md#1.2.2 @ 7de1a86"
related: []
level: acceptance
merged_from: "CHK-0005 @ 4c02731"
---

# Switching

click between two workspaces. Expect: nav, centre and right pane all follow; per-workspace state (nav mode, pins, follow mode) is remembered separately. — 2026-08-11, **against the running shell over CDP**, `project-os-cockpit` ⇄ `articles`. All three panes followed: nav `Open · 3 · PHASE-028…` → `PHASE-0001 Build audience · FEAT-0002…` (a different corpus entirely), centre → `articles`, context → `Decisions 10/13 accepted · ADR-0022…` → `No links from or to this note.` Switching back restored **project-os-cockpit's own** nav content and its `Features (by phase)` mode — remembered per workspace, not global. *Precisely: nav mode and nav state were exercised; **pins and follow mode were not** — the clause names three and two were driven. Recorded rather than rounded up.* (user:edwin, 2026-08-11)
