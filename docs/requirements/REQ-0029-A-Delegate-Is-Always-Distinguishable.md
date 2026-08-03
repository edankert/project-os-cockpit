---
type: "[[requirement]]"
id: REQ-0029
aliases: ["REQ-0029"]
title: "A delegate is always distinguishable from the human it acts for"
status: draft
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
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
