---
type: "[[change]]"
id: CHG-20260916-Name-active-agent-in-Needs-You-project-cards
title: "Name active agent in Needs You project cards"
status: merged
owner: user:edwin
created: 2026-09-16
updated: 2026-09-16
source: ["Edwin, 2026-09-16: while Codex works, the project-os-cockpit card in Needs You just shows working"]
commit: ""
pr: ""
impacts: ["[[SUR-0002]]"]
issues: ["[[ISS-0312]]"]
features: ["[[FEAT-0020]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[TST-0011]]", "[[CHG-20260916-Show-live-agent-in-Needs-You-headline]]"]
---

# Name active agent in Needs You project cards

## Summary
Needs You shows only “working…” for project cards created by record or publication work after an older agent request ages out. The mixed-session card already names Codex; the shared project status line will name the active agent too. Its age and cost suffixes remain unchanged.

## Impact

- [[SUR-0002]]: Needs You identifies Codex while it works on a project card, even when no agent approval or completed turn is pending.

## Documentation Coverage (All Types Considered)
Set each item to one of: `updated`, `new`, `not-applicable`, `deferred`.

- features: updated — [[FEAT-0020]] says every live project card names its agent.
- requirements: not-applicable — no requirement boundary changes.
- tasks: not-applicable — [[ISS-0312]] owns this follow-up.
- issues: updated — [[ISS-0312]] records the observed fallback card wording.
- tests: updated — a focused renderer check covers the record card and [[TST-0011]] records the live observation.
- workflows: not-applicable — no workflow changes.
- decisions: not-applicable — no architecture decision changes.
- risks: not-applicable — no new input or trust boundary.
- changes: new — this note records the correction.
- snapshot: updated — active work names the remaining fallback text issue.

## Follow-ups
- [x] Prefix the live agent name in the shared project status line without duplicating names already in hook messages. The focused renderer checks passed 8 cases.
- [x] Rebuild and reopen the independent Electron app. The project sidecar is healthy and the tmux-owned Codex process survived.
- [x] Edwin confirmed the reloaded card reads “Codex · working…” while this Codex turn runs.
