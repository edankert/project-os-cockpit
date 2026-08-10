---
type: "[[requirement]]"
id: REQ-0026
aliases: ["REQ-0026"]
title: "The cockpit performs only human-owned transitions"
status: "implemented"
phase: "[[PHASE-023-Levers-For-The-Human]]"
owner: user:edwin
created: 2026-08-03
updated: "2026-08-10"
source: ["[[DES-0005-The-Actuator-Grammar]]"]
priority: high
scope: "Every write path added by PHASE-023 and consumed by later phases"
specifies: ["[[FEAT-0059-The-Write-Service-Widens]]", "[[FEAT-0060-Transitions-And-Ticks-On-The-Note]]"]
acceptance:
  - "Every transition the cockpit offers appears in STATUSES.md's vocabulary and is a human judgment (approve, accept, decline, triage, answer) — never a close-out or gated status"
  - "Requesting an agent-owned transition is refused server-side with the ownership rule named, regardless of what any renderer displays"
  - "The transition vocabulary exists in exactly one module; no renderer restates it (guarded in the ISS-0023 style)"
  - "Removing a transition from the table removes it from every surface without a renderer change"
reviewed_by: "user:edwin"
review_date: "2026-08-03"
review_verdict: "plan-accepted"
---

# Only human-owned transitions

The line PHASE-007 drew and ADR-0007 crossed narrowly — *the cockpit writes only to record a decision a human made in the UI* — restated as an enforceable contract for the widened door. The agent's column of the ownership table is unreachable from the UI by construction, and the refusal is the server's, so no display bug can widen it.

## Acceptance Criteria

- [x] Every transition the cockpit offers appears in STATUSES.md's vocabulary and is a human judgment — never a close-out or gated status — evidence: test_every_status_in_the_table_exists_in_the_vocabulary and test_no_close_out_status_is_reachable_from_the_table — done/fixed/merged/implemented/passing/verified asserted absent (user:edwin, 2026-08-10)
- [x] Requesting an agent-owned transition is refused server-side with the ownership rule named, regardless of what any renderer displays — evidence: test_an_agent_owned_transition_names_the_rule — the refusal quotes REQ-0026, and stamp_transition is keyed on the note's CURRENT status so a stale renderer cannot replay a stale offer (user:edwin, 2026-08-10)
- [x] The transition vocabulary exists in exactly one module; no renderer restates it — evidence: test_the_actuator_row_declares_no_vocabulary — asserts the renderer names neither the statuses nor the verbs; the first cut styled by verb name and was corrected (user:edwin, 2026-08-10)
- [x] Removing a transition from the table removes it from every surface without a renderer change — evidence: the row is built from GET /api/notes/actions with no local list; legal_actions() is the only producer (user:edwin, 2026-08-10)
