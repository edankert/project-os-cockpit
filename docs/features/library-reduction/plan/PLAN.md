---
type: "[[plan]]"
title: "Library reduction — delivery plan"
status: done
owner: user:edwin
created: 2026-07-29
updated: 2026-07-29
implements: ["[[FEAT-0050-Library-Reduction]]"]
related: ["[[REQ-0025-No-Type-Loses-Its-Surface]]"]
---

# Library reduction — delivery plan

## Delivery sequence

1. **[[TASK-0243]]** — drop the Design and Decisions groups. Independent of everything else: both are duplicates of surfaces that already exist, so this can land first.
2. **[[TASK-0244]]** — workflows into the Docs tree: add `workflow` to `DOC_TREE_INLINE_TYPES`, remove `workflows` from `DOC_TREE_EXCLUDED_ROOTS`.
3. **[[TASK-0245]]** — drop Plans, Risks, Tests and Changes. **Blocked on [[FEAT-0046]], [[FEAT-0047]], [[FEAT-0048]] and [[FEAT-0049]]** — each removes the sole navigable route to its type.

## The ordering is the risk

[[REQ-0025]] exists because this is the one thing that can go wrong here, and nothing detects it: the validator checks the corpus, the tests check payload shape, and neither asks whether a rendered payload is reachable. Step 3 does not merge until its four destinations are done and their criteria ticked.
