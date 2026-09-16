---
type: "[[change]]"
id: CHG-20260915-Launch-Codex-in-inline-terminal-mode-for-scrollback
title: "Launch Codex in inline terminal mode for scrollback"
status: merged
owner: user:edwin
created: 2026-09-15
updated: 2026-09-15
source: ["[[ISS-0310]]", "[[TASK-0627]]", "Edwin, 2026-09-15: Codex output is still not reachable through the embedded terminal scrollback"]
commit: ""
pr: ""
impacts: ["desktop/src/ipc/agent-instrument.ts", "tests/test_agent_instrument.py"]
issues: ["[[ISS-0310]]"]
features: ["[[FEAT-0003]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[CHG-20260915-Implement-Codex-Terminal-Scrollback-Fix]]", "[[CHG-20260915-Fix-terminal-scrollback-and-Codex-exit-lifecycle]]"]
---

# Launch Codex in inline terminal mode for scrollback

## Summary
The embedded terminal will launch Codex in inline mode, so Codex output stays in xterm's normal scrollback and remains reachable with the mouse wheel. Claude keeps its existing alternate-screen behavior.

## Impact

No dedicated surface note exists for the embedded terminal in this repository. The visible change is recorded by [[FEAT-0003]] and [[ISS-0310]].

## Documentation Coverage (All Types Considered)
Set each item to one of: `updated`, `new`, `not-applicable`, `deferred`.

- features: updated — [[FEAT-0003]] now records Codex inline mode
- requirements: not-applicable — [[REQ-0005]]'s local-terminal boundary is unchanged
- tasks: updated — [[TASK-0627]] records the implementation and remaining live walk
- issues: updated — [[ISS-0310]] now identifies alternate-screen mode as the scrollback cause
- tests: updated — the wrapper regression test will require `--no-alt-screen`
- workflows: not-applicable — no project workflow changed
- decisions: not-applicable — this selects an existing Codex CLI option and adds no architecture decision
- risks: not-applicable — no dependency, credential, environment, or path contract changed
- changes: new — this change note
- snapshot: updated — the new change is recorded as active work

## Follow-ups
- [ ] Rebuild the Electron terminal and walk Codex scrollback in the cockpit.
- [ ] Confirm Codex exit returns to the shell without closing the cockpit.
