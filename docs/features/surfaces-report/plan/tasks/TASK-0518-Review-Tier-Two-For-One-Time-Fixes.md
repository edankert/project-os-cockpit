---
type: "[[task]]"
id: TASK-0518
aliases: ["TASK-0518"]
title: "Review Tier 2 check by check for one-time fixes that cannot regress"
status: backlog
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
parent: "[[FEAT-0131-The-Suite-Is-Refined]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# Review Tier 2 check by check for one-time fixes that cannot regress

158 checks, each referencing the `ISS-*` that created it. TESTING.md's default for Tier 2 is **never removed**, so the burden is on closing.

**No blanket rule.** A pass that retires Tier 2 wholesale is indistinguishable from losing the suite (REQ-0050 criterion 4).
