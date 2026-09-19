---
type: "[[change]]"
id: CHG-20260916-Deliver-live-Codex-approval-to-Needs-You
title: "Deliver live Codex approval to Needs You"
status: merged
owner: user:edwin
created: 2026-09-16
updated: 2026-09-16
source: ["Edwin, 2026-09-16: project icon shows Busy / working, but Needs You did not show a Codex Bash approval"]
commit: ""
pr: ""
impacts: ["[[SUR-0002]]"]
issues: ["[[ISS-0312]]"]
features: ["[[FEAT-0020]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[TST-0011]]"]
---

# Deliver live Codex approval to Needs You

## Summary
The project icon shows Codex work, but Edwin did not see the Bash approval in Needs You. The sidecar recorded `needs-input`; one request returned to `busy` after 55 ms, shorter than the desktop's five-second state-file poll. Electron main now forwards sidecar state events to the open renderer over its existing local event-stream connection.

## Impact

- [[SUR-0002]]: Needs You and the project icon receive each approval transition as it happens in the open project.

## Documentation Coverage (All Types Considered)
Set each item to one of: `updated`, `new`, `not-applicable`, `deferred`.

- features: updated — [[FEAT-0020]] describes immediate approval delivery for the open project.
- requirements: not-applicable — the existing agent attention contract stays in force.
- tasks: not-applicable — [[ISS-0312]] owns this correction.
- issues: updated — [[ISS-0312]] records the missed Bash approval and cause.
- tests: updated — [[TST-0011]] records the live failure and the focused bridge check.
- workflows: not-applicable — no project workflow changes.
- decisions: not-applicable — no architecture decision changes.
- risks: not-applicable — the bridge uses the existing local sidecar stream and IPC channel.
- changes: new — this note records the correction.
- snapshot: updated — active work records the missed approval and bridge repair.

## Follow-ups
- [x] Forward sidecar state events from Electron main to the open renderer without waiting for the file poll; a local stream test delivered `needs-input` and `busy` in order.
- [x] Rebuild and restart the independent Electron process; the sidecar health endpoint recovered and the tmux-owned Codex process survived.
- [ ] Verify the forwarded approval state and the Needs You card in the live app.
