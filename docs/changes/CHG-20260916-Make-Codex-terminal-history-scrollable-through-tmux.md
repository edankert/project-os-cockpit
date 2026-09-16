---
type: "[[change]]"
id: CHG-20260916-Make-Codex-terminal-history-scrollable-through-tmux
title: "Make Codex terminal history scrollable through tmux"
status: merged
owner: user:edwin
created: 2026-09-16
updated: 2026-09-16
source: ["[[ISS-0310]]", "Edwin, 2026-09-16: Document this and fix as suggested"]
commit: ""
pr: ""
impacts: ["[[SUR-0002]]"]
issues: ["[[ISS-0310]]"]
features: ["[[FEAT-0003]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[TASK-0627]]", "[[ISS-0161]]"]
---

# Make Codex terminal history scrollable through tmux

## Summary

People using Codex in the Electron console can open the history held by tmux and scroll it. The cockpit sends wheel input to tmux history when the program inside tmux uses its normal screen. It keeps the existing arrow-key behavior for an inner alternate-screen program and keeps direct mouse reports for programs that request them.

## Impact

- [[SUR-0002]]: The console offers a History action and lets the wheel move through Codex output held in tmux history while Claude keeps its own scrolling.

## Documentation Coverage (All Types Considered)
Set each item to one of: `updated`, `new`, `not-applicable`, `deferred`.

- features: updated — [[FEAT-0003]] names tmux as the history owner in the Electron console.
- requirements: not-applicable — [[REQ-0005]] governs local access, and the new action stays inside the existing terminal IPC boundary.
- tasks: updated — [[TASK-0627]] now includes history navigation and a live Codex, Claude, and shell comparison.
- issues: updated — [[ISS-0310]] records the tmux screen boundary and the remaining live verification.
- tests: updated — `desktop/tests/terminal-history.test.mjs` covers tmux history entry, wheel routing, and mouse state on reattachment; source checks cover the renderer action.
- workflows: not-applicable — no project workflow changes.
- decisions: not-applicable — tmux already owns persistent terminal history; this exposes that existing history.
- risks: not-applicable — no new credential, network listener, or external dependency is added.
- changes: new — this note records the visible change.
- snapshot: updated — active work and the affected surface are recorded.

## Follow-ups

- [ ] Walk a long Codex response, Claude mouse scrolling, and a plain shell in the rebuilt Electron console, including a workspace switch.
- [ ] Confirm that a Codex response missing from tmux history remains reachable in Codex's own transcript; that would require a separate transcript surface.
