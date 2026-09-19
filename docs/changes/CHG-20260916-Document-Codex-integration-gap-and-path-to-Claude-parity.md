---
type: "[[change]]"
id: CHG-20260916-Document-Codex-integration-gap-and-path-to-Claude-parity
title: "Document Codex integration gap and path to Claude parity"
status: merged
owner: user:edwin
created: 2026-09-16
updated: 2026-09-16
source: ["Review of the Codex and Claude integrations, 2026-09-16"]
commit: ""
pr: ""
impacts: ["tools/adapters/codex/ADAPTER.md", "docs/features/agent-hooks/FEAT-0019-Agent-Hook-Ingestion.md", "docs/features/agent-hooks/plan/tasks/TASK-0116-Codex-Hook-Injection.md"]
issues: ["[[ISS-0312]]"]
features: ["[[FEAT-0019]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[TASK-0116]]", "[[RISK-0004]]"]
---

# Document Codex integration gap and path to Claude parity

## Summary
The project notes now distinguish Codex's delivered `notify` feed from Claude's fuller lifecycle feed. A new issue records how native Codex hooks could close the gap and how to verify the result.

## Impact

- No screen changed: this change records a review and an implementation proposal; it does not change the cockpit or agent launch behavior.

## Documentation Coverage (All Types Considered)
Set each item to one of: `updated`, `new`, `not-applicable`, `deferred`.

- features: updated — [[FEAT-0019]] distinguishes the July delivery from the proposed native-hook follow-up
- requirements: not-applicable — no requirement or product behavior changes in this documentation update
- tasks: updated — [[TASK-0116]] records which checked claims the delivered implementation does not support
- issues: new — [[ISS-0312]] tracks the Codex lifecycle and adapter gap
- tests: deferred — [[ISS-0312]] defines live acceptance checks for a future implementation; no test is changed now
- workflows: not-applicable — no workflow changes now
- decisions: not-applicable — the installation scope remains a choice to settle during implementation
- risks: not-applicable — [[RISK-0004]] already covers hook injection, configuration, and trust; no new surface is installed now
- changes: new — this note records the documentation change
- snapshot: updated — [[ISS-0312]] and this change are registered without replacing the active terminal focus

## Follow-ups
- [ ] Settle how native hooks are loaded for cockpit-launched Codex without hiding user authentication or silently editing user configuration.
- [ ] Implement and walk the lifecycle feed described by [[ISS-0312]].
