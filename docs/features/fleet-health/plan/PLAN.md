---
type: "[[plan]]"
title: "Fleet health surface — delivery plan"
status: done
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
implements: ["[[FEAT-0028-Fleet-Health-Surface]]"]
related: ["[[FEAT-0018-Verification-Health-Surface]]", "[[PHASE-013-Fleet-Surfaces]]"]
---

# Fleet health surface — delivery plan

## Delivery sequence

1. **[[TASK-0248]]** — aggregate the signal for **live** workspaces. Pure reuse: each running sidecar already serves `GET /api/cockpit/validation` and publishes `cockpit:validation`. Main-process state map + IPC. Shippable alone, and it covers the workspaces anyone is actually looking at.
2. **[[TASK-0249]]** — **cold** workspaces, the expensive half. Needs a decision the feature note gets wrong (see below) and a cost bound; sequenced second so step 1 is not held up by it.
3. **[[TASK-0250]]** — the badge on the rail and tabs. Blocked on 1 for data, and on a **channel collision**: the rail entry already carries `.ws-dot` for agent state.
4. **[[TASK-0251]]** — the roll-up, deep-linking into each workspace's drift panel. Last: it is a view over 1 + 2.

## Two contradictions to settle before step 2

**Whose validator runs.** FEAT-0028's brief plan says *"run the repo's `tools/scripts/validate-docs.py`"*; `tools/scripts/validate-fleet.sh` already exists and says the opposite — *"uses THIS repo's validate-docs.py for uniform semantics"*. Those are different products: per-repo honours a repo that pinned an older template, uniform makes counts comparable. [[TASK-0249]] decides and records it; it must not be discovered at implementation time.

**The rail already has a dot.** `.ws-dot` is agent state (TASK-0082). A validator dot on the same element is a second signal on one channel — the budget problem [[DES-0004]] hit on the phase squares, in a smaller space. [[TASK-0250]] owns it.

## Read-only, and that is a constraint not a nicety

This feature *runs a script in ten other repositories*. Nothing in it may write to a repo it does not own, and [[TASK-0249]] carries that as a test rather than an intention.
