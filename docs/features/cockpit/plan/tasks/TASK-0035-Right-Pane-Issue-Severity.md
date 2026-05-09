---
type: "[[task]]"
id: TASK-0035
aliases: ["TASK-0035"]
title: "Cockpit: right-pane shows severity for issues (default 'low' when unspecified)"
status: done
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-09
updated: 2026-05-09
source: []
implements: ["[[FEAT-0006]]", "[[REQ-0013]]"]
fixes: []
effort: XS
due: ""
depends: []
blocks: []
related: []
tests: ["[[TST-0002]]"]
---

# TASK-0035 — Right-pane issue severity

## Definition of Done
- [x] Right-pane items where `type == "issue"` carry a `severity` field (lowercased) and a `priority: null`. Frontmatter `severity` wins; missing values default to `"low"`.
- [x] Non-issue items keep `priority` as before; their `severity` field is `null`.
- [x] JS `ctxItem` renders the severity chip when present, falling back to priority. Severity chip uses the existing `--severity-*` palette.
- [x] Tests cover both shapes: severity present, severity defaults to low.

## Steps
- [x] `_context_item` (cockpit.py) reads frontmatter severity for issue records, lowercases / defaults to `"low"`, and sets `priority` to `None` for issues.
- [x] `cockpit.js` `ctxItem` builds a `.ctx-severity[data-severity=…]` chip when `item.severity` is set; falls back to the existing `.ctx-priority` chip otherwise.
- [x] `cockpit.css` adds `.ctx-severity` rule (matching pill shape as `.ctx-priority`) keyed off the existing `--severity-{critical,high,medium,low}` tokens.
- [x] Tests: `test_context_payload_issue_carries_severity_with_default` (frontmatter `severity: high` survives) + `test_context_payload_issue_default_severity_low` (synthetic ISS with no severity → `"low"`). Plus assertion in `test_context_payload_item_columns` that non-issues have `severity: None`.

## Notes
Default chosen: `"low"`. Reasoning — issues filed without explicit severity are by default low-urgency; explicitly raising severity is a deliberate triage action.
