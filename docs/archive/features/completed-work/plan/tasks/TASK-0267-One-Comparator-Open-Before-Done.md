---
type: "[[task]]"
id: TASK-0267
aliases: ["TASK-0267"]
title: "One comparator sorts open before done, applied to items within every group, so state orders where no grouping axis can carry it"
status: done
phase: "[[PHASE-022-Completed-Work-Gets-Quieter]]"
owner: user:edwin
created: 2026-08-02
updated: 2026-08-02
source: ["[[FEAT-0056-Completed-Work-Ordering]]"]
parent: "[[FEAT-0056-Completed-Work-Ordering]]"
effort: S
depends: []
blocks: ["[[TASK-0268-Groups-With-Open-Work-Sort-First]]", "[[TASK-0269-The-Context-Pane-Stops-Filtering]]"]
related: ["[[ISS-0023-Status-Vocabulary-Drift]]"]
tests: ["[[TST-0023-Completed-Work-Ordering]]"]
---

# One comparator, open before done

## Definition of Done

- A single predicate derived from `statuses.COMPLETED_STATUSES` decides open vs done — not a second hand-written list, which is exactly the drift [[ISS-0023]] recorded across eight surfaces.
- Within a group, open items sort above completed ones; the existing order (ID, severity, path) survives as the tiebreak, so nothing shuffles that has no reason to.
- Applied wherever items are grouped: severity buckets, phase groups, and context-pane type groups.

## Notes

**Not** applied to the tasks view's groups, which group *by* status: sorting open-first inside a bucket labelled `done` is meaningless. The comparator's job is to carry state where the grouping axis cannot, and there the axis already carries it.

## Verification

A severity bucket containing both open and fixed issues renders the open ones first. Guard asserts it against a fixture with interleaved statuses.
