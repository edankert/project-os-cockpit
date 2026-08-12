---
type: "[[adr]]"
id: ADR-0010
aliases: ["ADR-0010"]
title: "What the browser cockpit is for — the read-only front door is the reading surface, and its view set follows from that rather than from history"
status: "proposed"
owner: user:edwin
created: 2026-08-09
updated: 2026-08-09
source: ["Session 2026-08-09: a review of every nav mode measured mode 1 exposing five views and mode 3 seven, with the browser missing all three question-answering surfaces"]
related: ["[[PHASE-029-One-Tool-Two-Front-Doors]]", "[[REQ-0032-Two-Front-Doors-Agree-Or-Differ-On-The-Record]]", "[[RISK-0001-Render-Server-Exposure]]", "[[REQ-0013-Cockpit-Three-Pane-Layout]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
---

# What the browser cockpit is for

## Context

The cockpit has two front doors onto the same sidecar:

- **Mode 1** — the render server's own HTML, bound to `0.0.0.0` so a tablet on the same Wi-Fi can read the notes. Views: `Project · Features · Tasks · Issues · Recent`.
- **Mode 3** — the Electron shell, Mac-local. Views: `Overview · Design · Features · Tasks · Issues · Review · Library`.

The gap was never decided. Mode 1 was the whole product until the shell arrived; every surface built since — the overview (PHASE-008), the design bench (PHASE-009), the review desk (FEAT-0041) — was built in the shell, and mode 1 kept the view set it had in May. `recent` is the proof that nothing is watching: it is a live button in `cockpit.js` and a member of `RETIRED_NAV_MODES` in `renderer.ts`, simultaneously.

So the question is not "should they match" but "what is the browser one *for*", which has never been written down.

## Options

1. **Deprecate mode 1.** Honest about where the effort goes; loses the tablet reader, which is a use Edwin has and the `0.0.0.0` bind exists to serve.
2. **Full parity.** Requires the desk and its write endpoints on a LAN-reachable surface. Refused: [[RISK-0001]]'s threat model is that the read surface must not become a write surface, and the loopback checks in `note_writes` are what keep the crossing honest.
3. **Mode 1 is the reading surface.** It gets every view that answers a question *without* asking the reader to change anything, and none of the actuating ones. The difference is then a property of the surface, not of its age.

## Decision (proposed)

**Option 3.** The browser cockpit is the **reading surface**: the whole record, legible, from a device that is not the Mac — and nothing that writes.

Consequences:

1. **It gets the Overview.** The overview is pure read, it is the surface that answers "where does this project stand", and it is the single most useful thing to have on a tablet. Its absence is the least defensible part of the current gap.
2. **It gets the Design register and artifacts, read-only.** Framing a design artifact is reading. The *verdict* controls are not, and stay out.
3. **It does not get the Review desk.** The desk exists to record human decisions, its endpoints refuse non-loopback callers, and a desk you cannot act on is a list of obligations you cannot discharge — worse than absent. A *read-only digest* of what is owed is a separate question, deferred to [[FEAT-0079]]'s authenticated path rather than smuggled in here.
4. **Every actuator stays mode-3.** No transition, tick, capture, verdict, or test run is reachable from the browser surface, regardless of what any renderer draws — enforced server-side, as it already is.
5. **The view set is declared once** and both renderers consume it, with each view marked as reading or actuating. A new view must be classified to exist; that is what stops the next silent divergence.

## Consequences

- `Recent`'s two verdicts resolve by the same rule: it is a reading view, so if it earns a place it earns it in both, and if it does not it goes from both. It cannot stay live in one and retired in the other.
- The shell keeps views the browser lacks, and that is now a stated property rather than a backlog item.
- This decision does not itself widen any surface. [[REQ-0032]] and [[PHASE-029]]'s exit criteria carry the guard, and [[RISK-0001]] is re-scanned before the phase closes.

## Acceptance

**Its own open threads, as criteria** ([[FEAT-0096]]). This decision is not a yes/no: it proposes Option 3 and leaves two things unsettled inside its own consequences. Each can be answered on its own, with evidence, from the note page — and accepting the ADR with either still open is allowed, because a person may take a decision while a thread stands and the record should show that rather than prevent it.

- [ ] **The read-only digest of what is owed:** consequence 3 defers it to [[FEAT-0079]]'s authenticated path rather than deciding it. Decide it, or record where it is deferred to and why that home is right.
- [ ] **`Recent`'s two verdicts:** the consequences resolve it *"by the same rule"* — a reading view lives in both surfaces or neither — without saying which it is. Say which.

## Status

`proposed`. This is the gate on [[PHASE-029]]: both features are shaped by which option is taken, so nothing there should start until it is decided.

*Updated 2026-08-12: the two criteria above are why this sat undecided. `Accept` stamped five consequences and both open threads in one click, and there was nowhere to say "yes to option 3, but not consequence 3 as written" ([[ISS-0152]]). Now there is — each thread is answerable on its own, and the verb itself can carry a sentence.*
