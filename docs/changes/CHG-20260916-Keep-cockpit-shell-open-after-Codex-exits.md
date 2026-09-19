---
type: "[[change]]"
id: CHG-20260916-Keep-cockpit-shell-open-after-Codex-exits
title: "Keep cockpit shell open after Codex exits"
status: merged
owner: user:edwin
created: 2026-09-16
updated: 2026-09-16
source: ["[[ISS-0311]]", "Edwin, 2026-09-16: exiting Codex must return to the normal command line without closing the cockpit"]
commit: ""
pr: ""
impacts: []
issues: ["[[ISS-0311]]"]
features: ["[[FEAT-0003]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[TASK-0627]]", "[[CHG-20260916-Trial-Codex-alternate-screen-display-in-the-Electron-console]]"]
---

# Keep cockpit shell open after Codex exits

## Summary
Exiting Codex in the embedded console leaves the same shell ready for the next command and keeps the cockpit window open. One new test confirms that the generated wrapper returns to the same shell after its Codex child exits. A second test confirms that a PTY exit sends a terminal event without calling Electron quit. The isolated Electron walk then confirmed the real Codex exit path ([[TASK-0627]]).

## Impact

- No screen changed: this change adds a regression check for existing terminal behavior.

## Documentation Coverage (All Types Considered)
Set each item to one of: `updated`, `new`, `not-applicable`, `deferred`.

- features: updated — [[FEAT-0003]] names the terminal exit behavior.
- requirements: not-applicable — the local-only terminal boundary does not change.
- tasks: updated — [[TASK-0627]] tracks the behavioral check and live walk.
- issues: updated — [[ISS-0311]] records the observed symptom and remaining live check.
- tests: updated — `desktop/tests/codex-shell-exit.test.mjs` runs the generated wrapper and returns to the same shell; `desktop/tests/terminal-history.test.mjs` checks that a PTY exit sends an event without quitting Electron.
- workflows: not-applicable — no project workflow changes.
- decisions: not-applicable — no architecture or policy decision changes.
- risks: not-applicable — no new security or external-system risk is introduced.
- changes: new — this note records the acceptance check for the exit path.
- snapshot: updated — the active issue and change are in canonical state.

## Follow-ups
- [x] Walk the rebuilt Electron cockpit: start Codex, use `/exit`, run a shell command, and confirm the window remains open ([[TASK-0627]]).
