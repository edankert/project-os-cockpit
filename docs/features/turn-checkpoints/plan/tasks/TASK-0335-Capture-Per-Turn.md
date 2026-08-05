---
type: "[[task]]"
id: TASK-0335
aliases: ["TASK-0335"]
title: "Capture the workspace at each turn boundary to a hidden ref — pruned by age and count, never pushed, never in history"
status: backlog
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-05
updated: 2026-08-05
source: ["[[FEAT-0078-Turn-Checkpoints]]"]
parent: "[[FEAT-0078-Turn-Checkpoints]]"
effort: L
depends: []
blocks: ["[[TASK-0336-The-Turn-Timeline]]"]
related: []
tests: []
---

# Capture per turn

## Definition of Done

- A turn boundary (the lifecycle event the agents strip already reads) captures the working tree to a checkpoint ref under a dedicated namespace — untracked files included, since an agent's damage is often a file it added.
- Refs live outside `refs/heads`, are excluded from every push path, and are pruned by age and count with the limits stated where they are set.
- Capture is best-effort and never blocks a turn: a failed capture is recorded and the session continues, because a supervision aid that can halt the work is worse than none.
- A repo with no checkpoints behaves exactly as today.
