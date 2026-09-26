---
type: "[[task]]"
id: TASK-0244
aliases: ["TASK-0244"]
title: "Workflows join the Docs tree, the way references already do"
status: done
phase: "[[PHASE-010-Surface-Ownership]]"
owner: user:edwin
created: 2026-07-29
updated: 2026-07-29
source: []
parent: "[[FEAT-0050-Library-Reduction]]"
effort: XS
depends: []
blocks: []
related: ["[[TASK-0036-Inline-References]]", "[[TASK-0037-Exclude-Canonical-Container-Dirs]]"]
tests: ["[[TST-0022-Surface-Ownership]]"]
---

# TASK-0244 — Workflows into the Docs tree

## Definition of Done
- [ ] `workflow` is in `DOC_TREE_INLINE_TYPES`
- [ ] `workflows` is out of `DOC_TREE_EXCLUDED_ROOTS`
- [ ] `workflow` is gone from `LIBRARY_RARE_TYPES`
- [ ] WF notes render in the Docs tree under a `workflows/` folder
- [ ] `workflow` stays in `_BY_TYPE_SKIP_IN_LIBRARY` explicitly

## Steps
- [ ] `DOC_TREE_INLINE_TYPES: tuple[str, ...] = ("reference", "workflow")`
- [ ] Drop `"workflows"` from `DOC_TREE_EXCLUDED_ROOTS` (`cockpit.py:167-190`)
- [ ] Drop `"workflow"` from `LIBRARY_RARE_TYPES`, add it to the explicit skip-set
- [ ] Test: the tree payload contains a `workflows` folder holding the WF notes

## Notes

The mechanism is the one references already use ([[TASK-0036]]) — typed notes joining the untyped tree via `extra_types`. Nothing new is invented.

The three WF notes in *this* repo are the untouched template drafts and are worth little; the type is not. Three of eleven fleet repos authored real workflows and every one of those is `status: active`. The upstream template shipping three drafts nobody fills in is a separate problem, owned by `~/Dev/repos/project-os/`.
