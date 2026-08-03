---
type: "[[design]]"
id: DES-0006
aliases: ["DES-0006"]
title: "The acceptance desk — a guided walk over a feature's criteria, where pass ticks with a witness and fail files the issue"
role: proposal
status: "accepted"
phase: "[[PHASE-024-Acceptance-Witnessed]]"
owner: user:edwin
created: 2026-08-03
updated: "2026-08-03"
source: ["Review 2026-08-03: the acceptance contract exists on paper (acceptance-tests template, tier rules, release gate) and has no surface; Edwin performed acceptance twelve times in PHASE-022 with no record beyond chat"]
asset: "DES-0006-acceptance-desk.html"
implements: []
supersedes: ""
superseded_by: ""
reviewed_by: "user:edwin"
review_date: "2026-08-03"
review_verdict: "plan-accepted"
related: ["[[FEAT-0063-The-Acceptance-Runner]]", "[[FEAT-0064-The-Acceptance-Gate]]", "[[REQ-0028-Evidence-Names-Its-Witness]]", "[[DES-0005-The-Actuator-Grammar]]"]
---

# The acceptance desk

## The model being extended, not invented

The review desk already runs **manual tests** step by step and `stamp_test_run` writes the outcome into the TST note — status, `last_run`, and a log under `## Runs`. Acceptance is that flow with three substitutions: the steps come from *requirements' acceptance criteria* instead of a TST's steps; pass writes a **tick with a witness** instead of a status; fail files an **issue** instead of just `failing`.

## Entry points

1. **The desk queue** gains `Awaiting your acceptance · N` — features carrying `acceptance: requested` (stamped by the agent at close-out when the feature opted in, [[FEAT-0064]]). Sits above `Changes requested`, because it is the queue's most human item.
2. **The feature note** — a `Start acceptance run` action in the actuator row ([[DES-0005]]), for accepting anything on demand, opted-in or not.

## The run

Centre pane, one criterion at a time — deliberately not a checklist page, because a list invites skimming and the runner's whole value is that each criterion was actually *tried*:

```
FEAT-0063 · Acceptance run                        3 of 7
──────────────────────────────────────────────────────────
REQ-0026 · criterion 2

  "A thought becomes a triaged issue without
   composing a prompt"

  [ Pass ]   [ Fail… ]   [ Skip / reconcile… ]   [ 📷 ]
```

- **Pass** → the criterion is ticked in the REQ through the [[DES-0005]] tick path, evidence auto-composed: `accepted in cockpit run, user:edwin, 2026-08-03` — [[REQ-0028]]'s witness, by construction.
- **Fail** → inline issue capture: title prefilled from the criterion, severity picker, one optional sentence. Creates the ISS via PHASE-023's create path, pre-linked to the REQ and feature, `status: open`. The run continues — a fail is a datum, not an abort.
- **Skip/reconcile** → the `[~]` form with its reason, for criteria overtaken by events.
- **📷** → attach a capture ([[FEAT-0066]]) to whatever the next verdict is.

## What a run leaves behind

Appended to the **feature** note under `## Acceptance runs`, in `stamp_test_run`'s log grammar:

```
### 2026-08-03 — user:edwin — 6 passed · 1 failed → ISS-0094 · 0 skipped
```

plus the ticks in the REQ notes themselves and any issues filed. If every criterion resolved and the feature carried `acceptance: requested`, the run stamps `accepted_by: user:edwin` / `accepted_date:` — the gate's satisfied state. The desk queue entry resolves through the existing `review-resolve` endpoint with the run as its outcome.

## The gate, precisely

`acceptance:` on a feature: absent (default — no gate), `requested` (queued, close-out may complete but the desk shows it owed), `accepted` (stamped by a completed run). A validator **warning** — not an error — when a `done` feature carries `requested` older than N days: the gate nags, it does not block, because a blocking gate on the one unautomatable judgment becomes a rubber stamp. Proposed upstream as the same pattern independent review took (warning first, ADR-0011's deadline mechanism if it earns it).

## Rejected alternatives

- **Acceptance as a TST subtype.** A test verifies behaviour; acceptance verifies *intent was met*, and its evidence is a person. Different question, different fields, same log grammar.
- **A separate acceptance app/page.** The desk is where obligations already live; a second desk splits the queue.
- **Blocking the close-out on acceptance.** The human being away for a week must not freeze the agent's pipeline; `requested` keeps the debt visible instead.
