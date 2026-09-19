---
type: "[[change]]"
id: CHG-20260916-Show-Codex-session-state-and-temperature-in-cockpit
title: "Show Codex session state and label unverified cache data"
status: merged
owner: user:edwin
created: 2026-09-16
updated: 2026-09-16
source: []
commit: ""
pr: ""
impacts: ["[[SUR-0002-The-Desktop-Console]]"]
issues: ["[[ISS-0312-Codex-Lifecycle-And-Adapter-Parity]]"]
features: ["[[FEAT-0019-Agent-Hook-Ingestion]]", "[[FEAT-0020-Agent-Activity-Surfaces]]", "[[FEAT-0081-What-A-Session-Costs-To-Keep-Alive]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: []
---

# Show Codex session state and label unverified cache data

## Summary
Codex sessions in the embedded terminal need to drive the same project status and attention views as Claude sessions. This change adds the missing lifecycle feed and separates the age of the last agent event from a measured prompt-cache temperature.

## Impact

- [[SUR-0002-The-Desktop-Console]]: The project icon and Needs you card show the current Codex session state, and the session detail names an agent's cache temperature only when that cache state is measured.

## Documentation Coverage (All Types Considered)
Set each item to one of: `updated`, `new`, `not-applicable`, `deferred`.

- features: updated
- requirements: not-applicable
- tasks: updated
- issues: updated
- tests: updated
- workflows: not-applicable
- decisions: not-applicable
- risks: updated
- changes: new
- snapshot: updated

## Follow-ups
- [ ] Record the live Codex walkthrough in [[TST-0011]] after the code path works.
- [ ] Keep exact Codex cache economics separate from this activity-status fix until a supported usage source is available in the embedded terminal.
