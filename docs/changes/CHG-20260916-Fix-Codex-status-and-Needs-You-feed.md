---
type: "[[change]]"
id: CHG-20260916-Fix-Codex-status-and-Needs-You-feed
title: "Fix Codex status and Needs You feed"
status: merged
owner: user:edwin
created: 2026-09-16
updated: 2026-09-16
source: ["Edwin, 2026-09-16: the project icon and Needs You still show no up-to-date Codex information"]
commit: ""
pr: ""
impacts: ["[[SUR-0002]]"]
issues: ["[[ISS-0312]]"]
features: ["[[FEAT-0019]]", "[[FEAT-0020]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[TST-0011]]", "[[RISK-0004]]"]
---

# Fix Codex status and Needs You feed

## Summary
New Codex sessions started from a refreshed cockpit shell can report prompt start, work, approval requests, turn completion, and exit to the project icon and Needs You. The active cockpit tmux shell retained its old `codex` function across app restarts, so its running Codex process still has only the `notify` callback. The newly generated lifecycle hook command also lacked shell quoting around the application-support path, which contains a space. The corrected wrapper uses a regenerated launcher file and quotes the hook command for both TOML and the shell.

## Impact

- [[SUR-0002]]: New Codex sessions started from a refreshed cockpit shell update the project icon and Needs You as prompts, tools, approvals, and completed turns occur.

## Documentation Coverage (All Types Considered)
Set each item to one of: `updated`, `new`, `not-applicable`, `deferred`.

- features: updated — [[FEAT-0019]] and [[FEAT-0020]] describe the live event path and its existing-shell limitation.
- requirements: not-applicable — no requirement boundary changes.
- tasks: not-applicable — [[ISS-0312]] owns this focused correction.
- issues: updated — [[ISS-0312]] records the observed live process arguments and hook-command defect.
- tests: updated — the generated Codex command is executed through a real shell and its lifecycle path is checked.
- workflows: not-applicable — no project workflow changes.
- decisions: not-applicable — no architecture decision changes.
- risks: updated — [[RISK-0004]] already covers hook trust and command execution; the quoting correction closes this failure mode.
- changes: new — this note records the correction.
- snapshot: updated — [[ISS-0312]] remains the active issue and records this regression.

## Follow-ups
- [x] Run a real ephemeral Codex CLI session with the quoted hook command. It fired `SessionStart`, `UserPromptSubmit`, `Stop`, and `SessionEnd`; this isolated probe bypassed hook trust and did not view the cockpit screen.
- [x] Verify the generated launcher through zsh and the decoded hook command through `/bin/sh`; the focused Node suite passed 5 checks and the focused sidecar suite passed 46.
- [x] Record that an already-running Codex process and its long-lived parent shell retain the old wrapper until the shell is refreshed.
- [x] After Edwin refreshed the shell and approved hooks, confirm the resumed process has seven hook flags and the sidecar records `needs-input` then `busy` for its native Codex session.
- [ ] Walk a new Codex process in the embedded terminal with normal hook trust and confirm the project icon and Needs You change on screen ([[TST-0011]]).
