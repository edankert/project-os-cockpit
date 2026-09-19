---
type: "[[change]]"
id: CHG-20260916-Revert-ineffective-Codex-alternate-screen-trial
title: "Revert ineffective Codex alternate-screen trial"
status: merged
owner: user:edwin
created: 2026-09-16
updated: 2026-09-16
source: ["[[ISS-0310]]", "Edwin, 2026-09-16: the Codex terminal shows no scrolling change during the alternate-screen trial"]
commit: ""
pr: ""
impacts: ["[[SUR-0002]]"]
issues: ["[[ISS-0310]]"]
features: ["[[FEAT-0003]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[TASK-0627]]", "[[CHG-20260916-Trial-Codex-alternate-screen-display-in-the-Electron-console]]"]
---

# Revert ineffective Codex alternate-screen trial

## Summary
Fresh cockpit shells started by the rebuilt app will use the prior inline setting again. Edwin's live comparison found no scrolling change from the alternate-screen trial. The running session received `tui.alternate_screen="always"`, but tmux still reported its pane on the normal screen, so the trial provided no observed benefit. Existing shells retain the function they loaded until they are refreshed.

## Impact

- [[SUR-0002]]: Codex started from a fresh cockpit shell uses the previous inline display setting, with the cockpit's tmux History action available for older output.

## Documentation Coverage (All Types Considered)
Set each item to one of: `updated`, `new`, `not-applicable`, `deferred`.

- features: updated — [[FEAT-0003]] records the trial outcome and restored setting.
- requirements: not-applicable — the local-only terminal boundary does not change.
- tasks: updated — [[TASK-0627]] closes the display-mode comparison and keeps the live scrolling check open.
- issues: updated — [[ISS-0310]] records the live tmux and process evidence.
- tests: updated — the Codex wrapper guard again requires `--no-alt-screen` and preserved notifications.
- workflows: not-applicable — no project workflow changes.
- decisions: not-applicable — this reverses an uncommitted experiment, not an architecture decision.
- risks: not-applicable — no new security or external-system risk is introduced.
- changes: new — this note records the trial result and rollback.
- snapshot: updated — canonical state records the result.

## Follow-ups
- [ ] Walk a fresh Codex session in the rebuilt cockpit and confirm older output remains reachable through tmux History.
