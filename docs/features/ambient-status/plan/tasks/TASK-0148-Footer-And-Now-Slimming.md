---
type: "[[task]]"
id: TASK-0148
aliases: ["TASK-0148"]
title: "Remove the footer agent dot; demote the Overview Now card to a one-liner"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-19
updated: 2026-07-19
source: []
parent: "FEAT-0031"
effort: ""
due: ""
depends: ["[[TASK-0147]]"]
blocks: []
related: []
tests: []
---

# TASK-0148 — footer + Now slimming

Delete `#sf-agent` (markup, `refreshFooterAgent`, CSS — including its missing-needs-input-style inconsistency, which disappears by deletion); footer keeps `#sf-sidecar` process health. Shrink `buildNowSection()` to a compact live-state line linking onward (strip focus now; `~agents` once FEAT-0032 lands). Depends on TASK-0147 so attention has its richer home before ambient copies are removed. Verification: live session shows state in exactly rail + strip; overview shows the one-liner.
