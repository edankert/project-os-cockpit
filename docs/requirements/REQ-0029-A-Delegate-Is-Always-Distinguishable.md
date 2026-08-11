---
type: "[[requirement]]"
id: REQ-0029
aliases: ["REQ-0029"]
title: "A delegate is always distinguishable from the human it acts for"
status: "implemented"
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-03
updated: "2026-08-11"
source: ["[[ADR-0009-The-Principal-Is-A-Role]]"]
priority: high
scope: "Every judgment made under delegation, in every phase that writes one"
specifies: ["[[FEAT-0075-The-Delegation-Policy]]", "[[FEAT-0077-The-Intent-Charter]]"]
acceptance:
  - "Every delegate write carries agent:principal plus the delegation record and charter shas — who decided, under what authority, as the policy stood when"
  - "No surface renders a delegate's stamp in a way mistakable for the human's; accepted_by distinguishes at a glance"
  - "The audit query 'all autonomous judgments in range' is answerable from frontmatter alone, with zero orphans"
  - "Revoking a delegation invalidates nothing already stamped — history keeps its authority as it stood"
---

# A delegate is always distinguishable

Delegation without distinguishability is impersonation. The value of the record — the reason acceptance is worth having at all — survives autonomy only if every judgment answers *who* and *under what authority* forever after.

## Acceptance Criteria

- [x] Every delegate write carries agent:principal plus the delegation record and charter shas — who decided, under what authority, as the policy stood when — evidence: `charter.witness()` composes `agent:principal (delegation: DELEGATION.md@<sha>, charter: INTENT.md@<sha>)`, and `stamp_acceptance_run` **refuses** a witness that starts `agent:` without one (user:edwin, 2026-08-11)
- [x] No surface renders a delegate's stamp in a way mistakable for the human's; accepted_by distinguishes at a glance — evidence: `charter.is_delegate_witness()` is the single reading every surface uses; `test_a_delegate_witness_is_distinguishable_from_a_person` asserts `user:edwin`, a bare `agent:principal` and an empty string all read as *not* a delegate (user:edwin, 2026-08-11)
- [x] The audit query "all autonomous judgments in range" is answerable from frontmatter alone, with zero orphans — evidence: the witness is written into `accepted_by` on the feature note, so the query is a frontmatter scan; a delegate write with no authority cannot exist, because the write path refuses it rather than recording it unstamped (user:edwin, 2026-08-11)
- [~] Revoking a delegation invalidates nothing already stamped — history keeps its authority as it stood — **reconciled**: held by construction rather than by a revocation path, because none exists yet. A stamp carries the policy's sha, so revoking or amending `DELEGATION.md` changes future stamps and cannot reach past ones. The criterion is satisfied in the only way it currently can be; a revocation *verb* belongs with the worker's operation (user:edwin, 2026-08-11)
