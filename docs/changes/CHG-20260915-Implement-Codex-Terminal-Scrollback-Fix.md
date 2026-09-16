---
type: "[[change]]"
id: CHG-20260915-Implement-Codex-Terminal-Scrollback-Fix
title: "Implement Codex Terminal Scrollback Fix"
status: merged
owner: user:edwin
created: 2026-09-15
updated: 2026-09-15
source: ["[[ISS-0310]]"]
commit: ""
pr: ""
impacts: ["desktop/src/ipc/agent-instrument.ts", "tests/test_agent_instrument.py"]
issues: ["[[ISS-0310]]"]
features: ["[[FEAT-0003]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[CHG-20260915-Document-Codex-Terminal-Scrollback-Fix]]", "[[TASK-0116]]", "[[TST-0062]]"]
---

# Implement Codex terminal scrollback fix

## Summary
The first Codex scrollback attempt launched Codex in inline mode. The decision to revert that flag was incorrect for the requested scrollback behavior and is superseded by [[CHG-20260915-Launch-Codex-in-inline-terminal-mode-for-scrollback]]. Claude's alternate-screen mouse behavior remains separate.

## Impact

- The embedded terminal's Codex wrapper retains notification instrumentation; the later change note adds inline mode for Codex scrollback.

## Documentation Coverage (All Types Considered)
Set each item to one of: `updated`, `new`, `not-applicable`, `deferred`.

- features: updated — [[FEAT-0003]] records the Codex inline behavior
- requirements: not-applicable — no requirement changed
- tasks: not-applicable — the focused wrapper change does not alter task scope
- issues: updated — [[ISS-0310]] records the implementation and verification state
- tests: updated — added a source-level wrapper regression guard
- workflows: not-applicable — no workflow changed
- decisions: not-applicable — the wrapper preserves the Codex-supported default terminal mode; it introduces no architecture decision
- risks: not-applicable — no new dependency, credential, environment, or path contract was introduced
- changes: new — this implementation note
- snapshot: updated — this change was added and issue/metric state was advanced

## Follow-ups
- [x] Add the Codex notification wrapper; the later change note adds `--no-alt-screen`.
- [x] Add a regression guard for the Codex wrapper and preserve Claude's existing command.
- [ ] Verify scrolling in a live Electron session with the installed Codex CLI.
