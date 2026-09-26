---
type: "[[change]]"
id: CHG-20260926-Released-Tickets-Move-To-The-Archive
title: "Tasks, issues and change notes finished at v1.0.0 move to docs/archive/"
status: merged
owner: user:edwin
created: 2026-09-26
updated: 2026-09-26
source: ["project-os-dev TASK-0186", "project-os-dev ISS-0091"]
commit: ""
pr: ""
impacts: []
issues: []
features: []
reviewed_by: ""
review_date: ""
review_verdict: ""
related: []
---

# Tasks, issues and change notes finished at v1.0.0 move to docs/archive/

## Summary

631 notes that were finished when v1.0.0 was released moved from `docs/` to `docs/archive/`, under the same path: 370 tasks, 132 issues and 129 change notes. Nothing was deleted, and git records each as a rename. Links to them still resolve by id, the validator reports only structural faults about them, and the repo's `.ignore` keeps them out of ripgrep and agent search (`rg --no-ignore docs/archive` still finds them).

## Impact

- No screen changed: the documentation corpus. The cockpit reads notes by id, and its full suite passes after the move (2205 passed).

## Documentation Coverage (All Types Considered)

- features: not-applicable
- requirements: not-applicable
- tasks: updated (moved)
- issues: updated (moved)
- tests: not-applicable
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: updated (moved) and new (this note)
- snapshot: updated (the moved items' entries dropped)

## Follow-ups

- Run `python3 tools/scripts/archive-notes.py` after each release to move that release's finished tickets.
