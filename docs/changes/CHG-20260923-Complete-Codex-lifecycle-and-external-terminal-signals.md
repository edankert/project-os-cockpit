---
type: "[[change]]"
id: CHG-20260923-Complete-Codex-lifecycle-and-external-terminal-signals
title: "Complete Codex lifecycle and external terminal signals"
status: merged
owner: user:edwin
created: 2026-09-23
updated: 2026-09-23
source: []
commit: ""
pr: ""
impacts: ["[[SUR-0002]]", "[[SUR-0005]]", "[[SUR-0006]]"]
issues: ["[[ISS-0312]]"]
features: ["[[FEAT-0019]]", "[[FEAT-0027]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: []
---

# Complete Codex lifecycle and external terminal signals

## Summary

Codex now forwards child lifecycle and interruption, keeps queued work held after interruption even when a background tool finishes, and submits queued prompts across workspace switches. New launchers use native hooks without injecting a legacy notify callback that could leave a ghost review session. A separate default-off setting enables signals from external Codex terminals. The shared adapter also reads quoted snapshot statuses correctly; the parser and regression were fixed in project-os and copied here.

## Impact

- [[SUR-0002]]: Queued Codex prompts now submit, and an interrupted turn holds the next queued task until a new user prompt or exit.
- [[SUR-0005]]: A separate Codex external-terminal setting explains the user hooks it installs and removes.
- [[SUR-0006]]: Codex interruptions remain visibly waiting for input after a background command finishes, and child completion leaves parent work active.

## Documentation Coverage (All Types Considered)

- features: updated — FEAT-0019 and FEAT-0027 describe the extension and retain the live-verification gate.
- requirements: not-applicable — no requirement criteria changed.
- tasks: new — TASK-0633 through TASK-0637 record the authorized sequence and evidence.
- issues: updated — ISS-0312 records implementation and remaining parity limits.
- tests: updated — TST-0010, TST-0011 and TST-0015 distinguish regression tests and partial live evidence.
- workflows: not-applicable — no new workflow entrypoint.
- decisions: not-applicable — PHASE-040 remains deferred; session ownership is unchanged.
- risks: updated — RISK-0004 records user-config preservation, event identity and trust coverage.
- changes: new — this note.
- snapshot: updated — focus returns to the incomplete live walk; derived statuses and counters are synchronized.

## Verification and remaining work

See [the verification report](../reference/codex-parity-verification-2026-09-23.md). This work has no new release-ledger verdict. No existing acceptance check names these changed screen behaviours, so no prior check verdict was invalidated. The historical TST-0011 e2e checklist remains active; it is not an acceptance-ledger check.

The complete live mixed-agent walk and fresh independent feature reviews remain owed. A disposable Claude profile could not complete a real turn because it reported Not logged in. Session usage and enforced reviewer budgets remain explicit limits.
