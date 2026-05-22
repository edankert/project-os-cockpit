---
type: "[[change]]"
id: CHG-20260522-Cockpit-Library-Changes-Group
aliases: ["CHG-20260522-Cockpit-Library-Changes-Group"]
title: "Cockpit: add Changes group to Project (Library) rare-types"
status: merged
owner: user:edwin
created: 2026-05-22
updated: 2026-05-22
source: ["[[TASK-0038]]"]
commit: ""
pr: ""
impacts:
  - "src/project_os_cockpit/cockpit.py"
  - "tests/test_cockpit.py"
issues: []
features: ["[[FEAT-0006]]"]
related: ["[[CHG-20260522-Cockpit-Exclude-Canonical-Container-Dirs]]"]
---

# Cockpit: Changes group in Project section

## Summary
Adds `"change"` to `LIBRARY_RARE_TYPES`, leading the rare-types list. Project (Library) mode now exposes a Changes group at the top, listing every change note with the standard id+title stacked card and the git-commit type icon.

## Impact

### `cockpit.py`
- `LIBRARY_RARE_TYPES` reordered to `(change, adr, release, risk, test, workflow, plan)` — change leads. Group label resolves to `"Changes"` via the existing fallback (`type_name.title() + "s"`); the `_pluralise_for_label` table doesn't need a new entry.

### Tests
- New `test_nav_payload_library_includes_changes_group` asserting `rare:change` exists, label is `"Changes"`, items use the stacked layout and carry `type: "change"`.
- 55 cockpit cases passing / 1 skipped (+1 net).

### Verified live (your-trainer/docs)
- Project → Changes group surfaces 129 entries (the full CHG corpus).
- Decisions (5) / Releases (9) / Risks (4) / Tests (10) / Workflows (1) follow underneath in their previous order.

## Follow-ups
- [ ] 129 items is a lot. If the Changes group dominates the Project pane visually, consider a "show recent N" cap with a "Show all" expand, mirroring the Recent-mode hard cap.

## Documentation Coverage (All Types Considered)
- features: not-applicable
- requirements: not-applicable
- tasks: new ([[TASK-0038]])
- issues: not-applicable
- tests: updated (`tests/test_cockpit.py`)
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new (this note)
- snapshot: updated (TASK 37→38, focus.task → TASK-0038, metrics tasks_total 37→38 / tasks_done 31→32, items.changes addition)
