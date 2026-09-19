---
type: "[[change]]"
id: CHG-20260916-Trial-Codex-alternate-screen-display-in-the-Electron-console
title: "Trial Codex alternate-screen display in the Electron console"
status: merged
owner: user:edwin
created: 2026-09-16
updated: 2026-09-16
source: ["[[ISS-0310]]", "Edwin, 2026-09-16: try the other suggested scrolling option after committing the working version"]
commit: ""
pr: ""
impacts: ["[[SUR-0002]]"]
issues: ["[[ISS-0310]]"]
features: ["[[FEAT-0003]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[TASK-0627]]", "[[CHG-20260916-Keep-tmux-scrolling-after-workspace-reattachment]]", "[[CHG-20260916-Revert-ineffective-Codex-alternate-screen-trial]]"]
---

# Trial Codex alternate-screen display in the Electron console

## Summary
The trial made newly spawned cockpit shells request Codex's alternate-screen display for comparison with Claude's fixed-prompt scrolling. The working inline-mode version remained in commit `17ca5b3`. Edwin launched Codex with the trial setting and saw no scrolling change, so the wrapper returned to the inline setting ([[CHG-20260916-Revert-ineffective-Codex-alternate-screen-trial]]).

## Impact

- [[SUR-0002]]: Codex launched from a new cockpit shell uses its full-screen display so the person can compare response scrolling and prompt position with Claude.

## Documentation Coverage (All Types Considered)
Set each item to one of: `updated`, `new`, `not-applicable`, `deferred`.

- features: updated — [[FEAT-0003]] records that Codex display mode is under comparison.
- requirements: not-applicable — the local-only terminal boundary does not change.
- tasks: updated — [[TASK-0627]] adds the live comparison and rollback decision.
- issues: updated — [[ISS-0310]] records the trial and its history trade-off.
- tests: updated — during the trial, the wrapper guard checked the alternate-screen request and notification option; the rollback restored the inline-mode assertion.
- workflows: not-applicable — no project workflow changes.
- decisions: not-applicable — this is an experiment, not a settled display-mode decision.
- risks: not-applicable — no new security or external-system risk; the possible loss of tmux scrollback is recorded in [[ISS-0310]].
- changes: new — this note records the reversible trial.
- snapshot: updated — the active issue and trial are in canonical state.

## Follow-ups
- [x] Start Codex with `tui.alternate_screen="always"` and compare response scrolling and prompt position.
- [ ] Switch projects and return, then check whether older Codex output remains reachable.
- [x] Revert the trial after Edwin reported no scrolling change ([[CHG-20260916-Revert-ineffective-Codex-alternate-screen-trial]]).

## Trial Result

Edwin started Codex and saw no scrolling change. The running Codex process had the `tui.alternate_screen="always"` argument, while tmux reported `alternate_on=0` and `mouse_any_flag=0` for its pane. The process and pane readings establish that the option reached Codex but did not produce the expected alternate-screen behavior in this session. They do not identify why Codex stayed on the normal screen. The trial is reversed to the working inline setting.
