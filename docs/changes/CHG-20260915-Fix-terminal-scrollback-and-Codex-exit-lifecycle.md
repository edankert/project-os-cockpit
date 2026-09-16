---
type: "[[change]]"
id: CHG-20260915-Fix-terminal-scrollback-and-Codex-exit-lifecycle
title: "Fix terminal scrollback and Codex exit lifecycle"
status: merged
owner: unassigned
created: 2026-09-15
updated: 2026-09-15
source: ["[[ISS-0310]]", "[[ISS-0311]]", "Edwin, 2026-09-15: terminal scrolling still fails for Claude, a normal shell and Codex; exiting Codex also appears to close the Electron cockpit"]
commit: ""
pr: ""
impacts: ["desktop/src/renderer/renderer.ts", "desktop/src/ipc/terminal.ts", "desktop/src/ipc/agent-instrument.ts", "desktop/src/main.ts"]
issues: ["[[ISS-0310]]", "[[ISS-0311]]"]
features: ["[[FEAT-0003]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: []
---

# Fix terminal scrollback and Codex exit lifecycle

## Summary
The embedded terminal will keep wheel scrolling usable for normal shells, Claude, and Codex, and ending Codex will leave the shell prompt in the cockpit. Claude's intentional alternate-screen mouse behavior remains enabled, and Codex uses inline mode so its output stays in xterm's scrollback. The Electron window and its sidecars will remain alive when the child command exits.

## Impact

<One line per screen this change altered: a `[[SUR-####]]` link, then a colon, then one sentence someone using the product would understand. A release walk's survey is built from these lines and reads nothing else (`tools/instructions/TESTING.md`, "The walk", rule 2). Draft them with an LLM from the diff and the repo's surface notes, then check that every id resolves.>

- Embedded Electron terminal: wheel scrolling reaches terminal history or the active TUI, and ending Codex returns to the shell prompt without closing the cockpit.

<A change that altered no screen writes the line below instead, with the reason. Keep one shape or the other, never both.>

No dedicated SUR note exists for the embedded terminal in this repository. FEAT-0003 and ISS-0310/ISS-0311 are the durable records for this visible behavior.

## Documentation Coverage (All Types Considered)
Set each item to one of: `updated`, `new`, `not-applicable`, `deferred`.

- features: updated — [[FEAT-0003]] records the scroll and command-exit behavior
- requirements: not-applicable — [[REQ-0005]]'s loopback-only boundary is unchanged
- tasks: new — [[TASK-0627]] owns the renderer and lifecycle repair
- issues: updated — [[ISS-0310]] carries the scrollback defect and [[ISS-0311]] carries the cockpit-exit defect
- tests: updated — source guards and terminal-path tests will cover wheel routing and child exit handling
- workflows: not-applicable — no project workflow changed
- decisions: not-applicable — existing xterm/PTY architecture remains in force
- risks: not-applicable — no new dependency, environment, credential, or path contract
- changes: new — this combined close-out note relates the two user-visible terminal repairs
- snapshot: updated — focus, counters, issue/task membership, and change membership are recorded

## Follow-ups
- [ ] Walk the rebuilt Electron terminal with a normal shell, Claude, and Codex, then confirm that Codex returns to the shell without closing the window.
