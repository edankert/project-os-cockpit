---
type: "[[change]]"
id: CHG-20260916-Show-live-agent-in-Needs-You-headline
title: "Show live agent in Needs You headline"
status: merged
owner: user:edwin
created: 2026-09-16
updated: 2026-09-16
source: ["Edwin, 2026-09-16: while Codex worked, Needs You said Claude is waiting for your input"]
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

# Show live agent in Needs You headline

## Summary
When Codex works while an older Claude session waits, Needs You shows the older Claude message as the project's headline, even though the project icon says Codex is busy. The card will name the live Codex activity first and keep Claude's waiting request on a second line. A current approval remains the primary message while it is pending.

## Impact

- [[SUR-0002]]: Needs You names the agent working in a project and keeps an older agent's pending review visible beneath it.

## Documentation Coverage (All Types Considered)
Set each item to one of: `updated`, `new`, `not-applicable`, `deferred`.

- features: updated — [[FEAT-0020]] states how a mixed-session card reads.
- requirements: not-applicable — the existing attention contract remains.
- tasks: not-applicable — [[ISS-0312]] owns this correction.
- issues: updated — [[ISS-0312]] records the observed mismatch.
- tests: updated — [[TST-0011]] tracks the live result and a focused mixed-session check.
- workflows: not-applicable — no project workflow changes.
- decisions: not-applicable — no architecture decision changes.
- risks: not-applicable — no new external inputs or trust boundaries.
- changes: new — this note records the correction.
- snapshot: updated — active work records the mixed-session wording issue.

## Follow-ups
- [x] Show live Codex work as the card headline while retaining Claude's waiting request below it. The mixed-session renderer check passed both the busy and approval cases.
- [x] Keep a dismissal stable as the displayed working duration grows; a new pending request still changes its key. Rebuilt Electron and reopened the project without ending the tmux-owned Codex process.
- [ ] Verify the mixed-session card after the desktop reload.
