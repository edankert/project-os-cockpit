---
type: "[[change]]"
id: CHG-20260509-Cockpit-Right-Pane-Issue-Severity
aliases: ["CHG-20260509-Cockpit-Right-Pane-Issue-Severity"]
title: "Cockpit: right-pane shows severity for issues (default 'low')"
status: merged
owner: user:edwin
created: 2026-05-09
updated: 2026-05-09
source: ["[[TASK-0035]]"]
commit: ""
pr: ""
impacts:
  - "src/project_os_cockpit/cockpit.py"
  - "src/project_os_cockpit/static/cockpit.js"
  - "src/project_os_cockpit/static/cockpit.css"
  - "tests/test_cockpit.py"
issues: []
features: ["[[FEAT-0006]]"]
related: ["[[REQ-0013]]"]
---

# Cockpit: right-pane issue severity

## Summary
Right-pane items for issue-typed notes now show the issue's **severity** chip instead of the requirement-flavoured **priority** chip. When frontmatter doesn't carry a severity, the chip defaults to `low`. Severity colours reuse the `--severity-{critical,high,medium,low}` tokens introduced for the issue group icons.

## Impact

### `cockpit.py`
- `_context_item` now branches on `record.note_type == "issue"`. When true, it reads `severity` from frontmatter (lowercased) or falls back to `"low"`, and sets `priority` to `None`. Non-issue items keep the previous priority shape and emit `severity: None`.

### `cockpit.js`
- `ctxItem` now builds a `<span class="ctx-severity" data-severity="…">` when `item.severity` is set. Falls back to the existing `<span class="ctx-priority">` otherwise.

### `cockpit.css`
- New `.ctx-severity` rule mirroring `.ctx-priority`'s pill shape. `.ctx-severity[data-severity="critical|high|medium|low"]` colour rules use the existing `--severity-*` tokens.

### Tests
- `test_context_payload_item_columns` extended to assert non-issues emit `severity: None`.
- New `test_context_payload_issue_carries_severity_with_default` — fixture's ISS-0001 (`severity: high`) appears in FEAT-0001 backlinks with the right severity + null priority.
- New `test_context_payload_issue_default_severity_low` — synthesises an ISS-0099 with no severity and asserts the default is applied.
- 52 cockpit cases passing / 1 skipped (was 50; +2).

### Verified live (your-trainer/docs)
- `curl /api/cockpit/context?this=FEAT-0036` returns ISS-0071/0072/0073 with `severity: "critical"` / `priority: null`.

## Documentation Coverage (All Types Considered)
- features: not-applicable
- requirements: not-applicable
- tasks: new ([[TASK-0035]])
- issues: not-applicable
- tests: updated (`tests/test_cockpit.py`)
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new (this note)
- snapshot: updated (TASK 34→35, focus.task → TASK-0035, metrics tasks_total 34→35 / tasks_done 28→29, items.changes addition)
