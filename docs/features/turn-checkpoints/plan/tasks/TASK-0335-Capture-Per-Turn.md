---
type: "[[task]]"
id: TASK-0335
aliases: ["TASK-0335"]
title: "Capture the workspace at each turn boundary to a hidden ref — pruned by age and count, never pushed, never in history"
status: done
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-05
updated: 2026-08-11
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

## Done — 2026-08-11

`src/project_os_cockpit/checkpoints.py` — capture, list, prune.

Built now, ahead of the rest of [[PHASE-027]], because it is a **mitigation for [[RISK-0006]] rather than a part of the hazard**. The risk's first shape is compounding judgment; the only unit of undo today is the close-out commit — the whole session or nothing. This makes the unit a turn.

Three properties carry the safety, each a way this could be worse than useless:

- **Outside every push path.** `refs/cockpit/turns/` — not `refs/heads` (pushed by default, and a hundred turn refs in `git branch` is a tool nobody keeps) and not `refs/tags`. A checkpoint is taken automatically dozens of times an hour; publishing is a deliberate act.
- **Untracked files included.** An agent's damage is often a file it *added*, and a checkpoint capturing only tracked changes would restore a tree still carrying it.
- **The real index untouched.** Capture runs against a temporary `GIT_INDEX_FILE`, so an agent mid-`git add` does not have its staging area rewritten by a checkpoint it did not ask for. A safety net that edits your staging area is a second actor, not a net.

Pruning is stated where it is set (`MAX_CHECKPOINTS = 200`, roughly a day of hard use) rather than in a config nobody reads.

[[TASK-0336]] (the turn timeline) and [[TASK-0337]] (principal-owned restore) remain, and 0337 is deliberately not built yet: restore is the verb that can *lose* work, and [[ADR-0009]] makes it principal-owned — it belongs with the rest of PHASE-027's approvals rather than ahead of them.
