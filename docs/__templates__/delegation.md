---
type: "[[reference]]"
title: "Delegation policy"
status: draft
owner: unassigned
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# Delegation policy

**Everything below is commented out on purpose. An empty policy delegates nothing** — that is the safe default and it is the one this file ships with. Uncommenting a line is the act of delegating; there is no line to delete to *withhold* authority, because withholding is the state you start in.

This note is consulted **only when its `status:` is `approved`**, and it is approved through the actuator row by the principal (ADR-0009 §4). A `draft` policy is no policy.

## Delegations

Format: `- judgment: <what> → <to whom> [threshold: <when>]`

The `to` may be a specific delegate (`agent:principal`) or `any-delegate`.

<!--
- judgment: triage issues → agent:principal [threshold: severity below high]
- judgment: close tasks → agent:principal
- judgment: draft release notes → agent:principal
-->

## Escalations

Format: `- kind: <queue kind> timeout: <hours> default: <assumption>`

A kind with no line here has **no timeout** and falls to the alarm path — see `escalation.py`. Nothing waits silently either way.

<!--
- kind: question timeout: 24 default: proceed on the stated assumption
-->

## What is never delegated

Recorded here rather than assumed, so the list is readable rather than inferred from what is absent:

- **Accepting a design or a requirement.** `HUMAN_TRANSITIONS` refuses these to an agent regardless of this file; the policy cannot widen what the server denies.
- **Answering a permission prompt** (ISS-0094) — the prompt exists because a different party decides.
- **Rewinding a turn checkpoint** (ADR-0009, FEAT-0078) — a worker that can undo its own turns can erase the evidence of going wrong.
- **Pushing.** ADR-0009 named it so it could not relax as a side effect; TASK-0328's ADR is where it may relax *as a decision*.
