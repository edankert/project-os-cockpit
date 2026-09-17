---
type: "[[change]]"
id: CHG-20260916-Keep-walk-options-behind-one-control
title: "Keep walk options behind one control"
status: merged
owner: user:edwin
created: 2026-09-16
updated: 2026-09-16
source: ["Your Trainer FEAT-0122 B3–B4: one current action and secondary navigation on demand; real Chrome rendering of the Android walk, 2026-09-16"]
commit: ""
pr: ""
impacts: ["[[SUR-0004-The-Release-Walk]]"]
issues: []
features: ["[[FEAT-0151-The-Release-Walk-Has-One-Next-Action]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[TASK-0629-Show-One-Walk-Action-And-Its-Readiness]]"]
---

# Keep walk options behind one control

## Summary
The release walk keeps the current session and action in view while placing occasional navigation under Walk options. A Chrome render of the Android payload at desktop and narrow widths shows one compact navigation row above the action. The session's starting state and equipment sit inside required setup after the first step, and evidence fields follow the selected light or dark theme.

## Impact

- [[SUR-0004-The-Release-Walk]]: Step and session navigation remain available under Walk options; starting state and equipment move into required setup, and evidence inputs match the selected theme.

## Documentation Coverage (All Types Considered)
Set each item to one of: `updated`, `new`, `not-applicable`, `deferred`.

- features: updated
- requirements: not-applicable
- tasks: updated
- issues: not-applicable
- tests: updated
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new
- snapshot: updated

## Follow-ups
- [x] Move occasional controls into Walk options while keeping Review results and the current step visible.
- [x] Exercise navigation in the focused renderer test and render the current Android payload in headless Chrome at 1100 and 700 pixels wide. This is a standalone browser harness; a full Electron walk remains under TASK-0631.
- [x] Put session state and equipment in the required-setup disclosure and verify that later steps can reopen them. The 77-case renderer suite and a narrow Chrome render confirm the later step keeps setup available without repeating it above the action.
