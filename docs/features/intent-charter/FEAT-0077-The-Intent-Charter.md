---
type: "[[feature]]"
id: FEAT-0077
aliases: ["FEAT-0077"]
title: "The intent charter — DES-0003's page graduated into the oracle a delegated acceptance judges against"
status: done
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[DES-0009-The-Standing-Worker]]", "[[DES-0003-Intent-Page-And-Claims-Board]]"]
goal: "A durable charter — goals, non-goals, taste constraints — that the delegated principal reads before judging; the delegated flavour of the acceptance runner, clean-context and charter-bound; and DES-0003 revised for this role and offered for acceptance."
requirements: ["[[REQ-0029-A-Delegate-Is-Always-Distinguishable]]"]
tasks:
  - "[[TASK-0332-DES-0003-Revised]]"
  - "[[TASK-0333-The-Charter-Note]]"
  - "[[TASK-0334-Delegated-Acceptance]]"
release: "[[REL-0001-The-Human-Has-Levers]]"
related: ["[[FEAT-0063-The-Acceptance-Runner]]"]
tests: []
---

# The intent charter

## Goal

Acceptance asks *is this what I asked for?* — so a delegate needs the asking written down. The charter is that artifact: what the project is for, what it must never become, and the taste rules twelve PHASE-022 corrections taught (fold on volume never meaning, one border per object, names are not labels…). A delegated acceptance run is FEAT-0063's runner with the witness `agent:principal`, the charter in context, and clean-context separation from the worker whose output it judges — ADR-0013's standard applied to the second gate.

## Out of Scope

- The charter writing itself. An agent drafts from the corpus's recorded decisions; the principal approves — the FEAT-0070 discipline.
- Making delegated judgment as good as Edwin's. The phase bounds and audits it; the charter is how it improves.

## Acceptance

- [x] An `INTENT.md` exists per repo — what this is for, what it must never become, and the taste its record has paid for ([[TASK-0333]])
- [x] **Drafted from the corpus, never invented** — every clause quotes or cites the ADR, close-out or design note it came from, so a reader can check rather than trust
- [x] Only an **approved** charter is usable; a draft charter is no charter, and an incomplete one is refused with the missing section named
- [x] Amendment re-enters approval **by construction** — any edit changes the sha, so a judgment cannot inherit a standard that moved
- [x] A delegated run's witness names the charter and delegation shas, and a bare `agent:principal` is **refused** ([[TASK-0334]], [[REQ-0029]])
- [x] `accepted_by` distinguishes delegate from human at a glance, through one reading no surface re-derives
- [x] [[DES-0003]]'s oracle role is discharged by the charter; [[DES-0009]] gains the artifact that lets it be offered ([[TASK-0332]])

## Verification

`tests/test_charter.py` — 9 tests. Four cover the ways a charter can fail to be usable (absent, draft, incomplete, edited), because *"partially useful"* is not a state a standard can be in: a delegate reading half a charter has no way to know which half.

**The charter itself is `draft`** and `charter.load()` says so. Approving it is the principal's, and no delegated judgment may cite it until then — which is the same gate the delegation policy passes through, for the same reason.
