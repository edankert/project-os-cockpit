---
type: "[[change]]"
id: CHG-20260916-Finish-PHASE-004-terminal-scrollback-and-Codex-exit
title: "Finish PHASE-004 terminal scrollback and Codex exit"
status: merged
owner: user:edwin
created: 2026-09-16
updated: 2026-09-16
source: ["[[TASK-0627]]", "Edwin, 2026-09-16: finish PHASE-004 terminal work before upstreaming the Codex project adapter"]
commit: ""
pr: ""
impacts: []
issues: ["[[ISS-0310]]", "[[ISS-0311]]"]
features: ["[[FEAT-0003]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[PHASE-004-Embedded-Terminal]]"]
---

# Finish PHASE-004 terminal scrollback and Codex exit

## Summary
The console finish pass verified that earlier output remains reachable through tmux history and that exiting Codex returns to the shell without closing the cockpit. It closes the existing terminal task before Codex adapter work moves upstream.

## Impact

- No screen changed: the terminal behavior was implemented in the earlier PHASE-004 changes; this pass adds tests and records live verification of that behavior.

## Documentation Coverage (All Types Considered)
Set each item to one of: `updated`, `new`, `not-applicable`, `deferred`.

- features: updated — [[FEAT-0003]] records the terminal behavior and its live verification.
- requirements: not-applicable — [[REQ-0005]] still defines the local-only boundary.
- tasks: updated — [[TASK-0627]] owns the terminal finish pass.
- issues: updated — [[ISS-0310]] and [[ISS-0311]] record the observed results.
- tests: updated — the terminal history and Codex shell-exit tests pass; a live walk used real Codex and Claude CLIs in an isolated Electron copy.
- workflows: not-applicable — no project workflow changes.
- decisions: not-applicable — [[ADR-0002]] remains the terminal architecture.
- risks: not-applicable — no new trust or network boundary is introduced.
- changes: new — this note records completion of the existing terminal task.
- snapshot: updated — [[TASK-0627]] and its issues are resolved in canonical state.

## Follow-ups
- [x] Record the live terminal walk on [[TASK-0627]] and close [[ISS-0310]] and [[ISS-0311]].
