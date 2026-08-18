---
type: "[[task]]"
id: TASK-0503
aliases: ["TASK-0503"]
title: "Replace the sixty-row blocking wall with a breakdown by area, each part linking to a filtered `~checks`"
status: backlog
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
parent: "[[FEAT-0125-The-Release-Page-Reports-What-Holds-It]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# Replace the sixty-row blocking wall with a breakdown by area, each part linking to a filtered `~checks`

The verdict line and confidence roll-up stay. `gate.blocking` carries `area` on every row, so the breakdown is a tally over data already in the payload.

Lossless: the full list stays reachable through the links, and the count in the heading must equal the number of rows behind them.
