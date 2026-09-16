---
type: "[[change]]"
id: CHG-20260915-Restore-terminal-scrolling-after-workspace-reattachment
title: "Restore terminal scrolling after workspace reattachment"
status: merged
owner: user:edwin
created: 2026-09-15
updated: 2026-09-15
source: ["[[ISS-0310]]", "Edwin, 2026-09-15: Claude and Codex terminal scrolling stopped after the shared renderer reset xterm mouse mode"]
commit: ""
pr: ""
impacts: ["desktop/src/renderer/renderer.ts", "tests/test_view_landings.py"]
issues: ["[[ISS-0310]]"]
features: ["[[FEAT-0003]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[ISS-0016]]", "[[ISS-0160]]", "[[ISS-0161]]", "[[CHG-20260915-Implement-Codex-Terminal-Scrollback-Fix]]"]
---

# Restore terminal scrolling after workspace reattachment

## Summary
Workspace switching now restores mouse-wheel forwarding for a still-running alternate-screen terminal such as Claude. Plain shells and inline Codex keep xterm's own scrollback, and a detached TUI that has exited cannot leave stale mouse reporting enabled.

## Impact

- Embedded Electron terminal: switching workspaces keeps Claude's wheel scrolling live without sending stale mouse reports to a plain shell.

(No surface link is available: this repository has no surface note for the embedded terminal. The existing feature note is the durable product record.)

## Documentation Coverage (All Types Considered)
Set each item to one of: `updated`, `new`, `not-applicable`, `deferred`.

- features: updated — FEAT-0003 records the shared renderer repair
- requirements: not-applicable — REQ-0005's local-terminal boundary is unchanged
- tasks: not-applicable — this is a regression repair under existing terminal tasks
- issues: updated — ISS-0310 now records the shared renderer cause and fix
- tests: updated — the renderer guard now covers safe mouse-mode restoration
- workflows: not-applicable — no workflow changed
- decisions: not-applicable — no new architecture decision; the restore is bounded by xterm's existing buffer state
- risks: updated — stale mouse reports are prevented while the scroll regression is removed
- changes: new — this note
- snapshot: updated — active issue and change membership recorded

## Follow-ups
- [ ] Walk the rebuilt Electron terminal with Claude alternate-screen mode, Codex inline mode, and a plain shell.
- [ ] Close ISS-0310 after the live walk passes.
