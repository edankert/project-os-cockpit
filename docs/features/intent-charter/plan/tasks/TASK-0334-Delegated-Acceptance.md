---
type: "[[task]]"
id: TASK-0334
aliases: ["TASK-0334"]
title: "Delegated acceptance — the runner with agent:principal as witness, charter in context, worker kept at arm's length"
status: done
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[FEAT-0077-The-Intent-Charter]]"]
parent: "[[FEAT-0077-The-Intent-Charter]]"
effort: L
depends: ["[[TASK-0333-The-Charter-Note]]"]
blocks: []
related: ["[[REQ-0029-A-Delegate-Is-Always-Distinguishable]]"]
tests: []
---

# Delegated acceptance

## Definition of Done

- A delegated run is FEAT-0063's runner driven by a principal-agent session: clean context (never the worker's session or its reasoning trace — ADR-0013's standard), the approved charter in context, judging against criteria by using the product where the criteria demand it.
- Every tick's witness is `agent:principal` with charter and delegation shas; `accepted_by` distinguishes delegate from human at a glance (REQ-0029).
- Fails file issues exactly as human runs do; the digest lifts delegate-accepted features for the human's spot-check — supervision is reading.

## Done — 2026-08-11

`charter.witness()` composes a delegated attribution, and `stamp_acceptance_run` **refuses a delegate that cannot name its authority**.

[[REQ-0029]]'s sentence is the test: *delegation without distinguishability is impersonation.* So `agent:principal` **alone is refused** — an attribution that could be confused with a person's is the entire failure. A delegated acceptance must carry both shas:

```
agent:principal (delegation: DELEGATION.md@<sha>, charter: INTENT.md@<sha>)
```

`is_delegate_witness()` gives every surface one reading of "was this a person?", so `accepted_by` distinguishes delegate from human **at a glance** rather than by lookup — and no surface re-derives the rule.

**A human run is unaffected**, which needed its own test: the guard must not make a person carry a charter they are not acting under, because a human accepts on their own authority.

The charter's sha covers the **whole note** deliberately. A change anywhere is a change to the standard, and pinning only the sections would let the surrounding prose drift under judgments already made against it — the same reasoning `design_revision` uses for [[ISS-0056]].
