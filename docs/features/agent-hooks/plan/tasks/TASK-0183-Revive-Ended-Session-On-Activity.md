---
type: "[[task]]"
id: TASK-0183
aliases: ["TASK-0183"]
title: "Revive an agent session on fresh activity, so a terminal that survives a sidecar soft-reload is not stuck reading `ended`"
status: done
phase: "[[PHASE-005-Desktop-Shell]]"
owner: user:edwin
created: 2026-07-21
updated: 2026-09-07
source: ["[[ISS-0014]]"]
parent: "FEAT-0019"
effort: ""
due: ""
depends: []
blocks: []
related: ["[[TASK-0184]]"]
tests: []
---

# Revive an ended session on activity

*Reconstructed 2026-09-07 ([[ISS-0287]]). This note was committed as a **zero-byte file** on 2026-07-21 and stayed empty, so every citation of it resolved to nothing and it was absent from the snapshot and every count. What follows is taken from the delivering commit `15d732c` and from the issue it closed — nothing here is inferred beyond what those record.*

## What it did

A sidecar soft-reload marked the session `ended` while the terminal underneath it kept running — tmux outlives the sidecar ([[TASK-0144]]) — so the strip showed a dead session and its live cost and context stopped updating. Fresh activity on a session now revives it rather than being read as noise against a terminal state.

It closed [[ISS-0014]] and shipped beside [[TASK-0184]], which fixed the neighbouring bleed: one workspace's last prompt surviving a switch into another.

## Verification

Carried by the batch's own review; no test note is claimed, because none was written at the time and inventing one now would be a false record.
