---
type: "[[task]]"
id: TASK-0479
aliases: ["TASK-0479"]
title: "Pilot: this repo's 34 checks, with the gate and the view walked afterwards"
status: backlog
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
source: ["[[FEAT-0119-The-Merge-Migration]]"]
parent: "[[FEAT-0119-The-Merge-Migration]]"
effort: M
depends: ["[[TASK-0478-Renumber-Into-The-TST-Space]]", "[[TASK-0488-Drop-The-Feature-Tests-Field-And-The-Path-Fallback]]"]
blocks: []
related: []
tests: []
---

# Pilot: this repo

34 checks, 0 blocking, all settled — the smallest suite in the fleet and the one whose corpus this session knows best. Migrate, assert parity through the reader, then **walk the surfaces**: the Tests navigator groups, the `~checks` page, the release gate, the sweep, and the Publication view's acceptance subgroup.

**The badge is the first thing to check, not the last** — [[REQ-0037-The-Badge-Never-Admits-Acceptance-Tests]]. This repo's Tests badge reads 1 on 2026-08-18. If it reads 35 afterwards, stop and do not proceed to the fleet.

Done when: parity green, badge unchanged at 1, the gate still reports 0 blocking, and every acceptance surface renders from the merged notes.
