---
type: "[[change]]"
id: CHG-20260916-Keep-tmux-scrolling-after-workspace-reattachment
title: "Keep tmux scrolling after workspace reattachment"
status: merged
owner: user:edwin
created: 2026-09-16
updated: 2026-09-16
source: ["[[ISS-0310]]", "Edwin, 2026-09-16: scrolling becomes limited or stops after leaving and returning to a project"]
commit: ""
pr: ""
impacts: ["[[SUR-0002]]"]
issues: ["[[ISS-0310]]"]
features: ["[[FEAT-0003]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[TASK-0627]]", "[[CHG-20260916-Make-Codex-terminal-history-scrollable-through-tmux]]"]
---

# Keep tmux scrolling after workspace reattachment

## Summary
Codex history remains reachable by the wheel after leaving and returning to a project in the Electron cockpit. The wheel now chooses tmux history from the workspace's tmux backing, not from the terminal view's reconstructed screen type. Claude keeps its existing direct mouse path.

## Impact

- [[SUR-0002]]: Returning to a project still lets the console wheel reach the same retained Codex and shell history as before the switch.

## Documentation Coverage (All Types Considered)
Set each item to one of: `updated`, `new`, `not-applicable`, `deferred`.

- features: updated — [[FEAT-0003]] states that tmux history must remain reachable after a workspace switch.
- requirements: not-applicable — the existing local terminal boundary remains unchanged.
- tasks: updated — [[TASK-0627]] tracks the reattachment regression and its live check.
- issues: updated — [[ISS-0310]] records Edwin's post-restart observation and the cause.
- tests: updated — a regression check covers wheel routing when the replayed xterm buffer is normal but tmux still owns history.
- workflows: not-applicable — no project workflow changes.
- decisions: not-applicable — this repairs the existing tmux-history behavior without a new architecture choice.
- risks: not-applicable — no new service, credential, or external dependency is added.
- changes: new — this note records the repaired user-visible behavior.
- snapshot: updated — the active issue and this change remain in canonical state.

## Follow-ups
- [ ] Walk a long Codex session before and after switching projects, then compare Claude scrolling in the same build.
- [ ] Decide separately whether Codex should use its own alternate-screen interface to keep its prompt fixed like Claude.
