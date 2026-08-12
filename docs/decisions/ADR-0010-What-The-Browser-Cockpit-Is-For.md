---
type: "[[adr]]"
id: ADR-0010
aliases: ["ADR-0010"]
title: "What the browser cockpit is for — the read-only front door is the reading surface, and its view set follows from that rather than from history"
status: "accepted"
owner: user:edwin
created: 2026-08-09
updated: "2026-08-12"
source: ["Session 2026-08-09: a review of every nav mode measured mode 1 exposing five views and mode 3 seven, with the browser missing all three question-answering surfaces"]
related: ["[[PHASE-029-One-Tool-Two-Front-Doors]]", "[[REQ-0032-Two-Front-Doors-Agree-Or-Differ-On-The-Record]]", "[[REQ-0034]]", "[[RISK-0001-Render-Server-Exposure]]", "[[RISK-0005-The-Write-Surface]]", "[[REQ-0027]]", "[[ADR-0022]]", "[[REQ-0013-Cockpit-Three-Pane-Layout]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
decided_option: "4"
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
4. **Parity, gated on an authenticated write path.** The same functionality on every surface — the goal option 2 wanted — but reached by building the thing option 2 assumed away. Writes stay loopback-only until a surface can prove *who* is asking; then the loopback check is replaced by that proof rather than removed, and parity follows for every verb at once.

## Decision

**Option 4**, decided 2026-08-12. **Parity is the goal; authentication is its precondition.**

The browser cockpit is the reading surface *for now*, and that is a **stage rather than a property** — which is the whole difference from what this note proposed for three days.

### How this changed

It proposed **option 3** on 2026-08-09 and everything below the fold was written for option 3. On 2026-08-12 Edwin accepted it as **option 2** — full parity — on the ground that *"we want to be able to support the same functionality across multiple surfaces… not sure how much of a concern the security issues raised are when used within very clear boundaries"*, and invited pushback. The pushback, and his agreement with it, is what option 4 is.

### Why option 2 could not be taken as written

**The loopback check is not a safety feature on top of an authorisation model. It IS the authorisation model.** There is no authentication anywhere in this tool. [[REL-0001]]'s acceptance pass drove every mutation endpoint over the real LAN interface: **ten of ten returned 403 while reads returned 200** ([[REQ-0027]], [[RISK-0005]]). Take that check away and the question *"who is allowed to write here"* has no answer at all — every device on the Wi-Fi can transition notes, tick criteria and create files across twelve repos.

**A LAN is a boundary a router advertises; loopback is one the OS enforces.** "Clear boundaries" is doing more work in option 2 than it looks: a guest phone, an IoT device or one compromised laptop is inside them.

**One of those repos publishes a website.** `your-applications.com`'s only remote is a deploy target, which is why pushing it is refused everywhere in this tool. Unauthenticated LAN *writes* against a git repo are a different risk class from unauthenticated LAN *reads*.

**And [[ADR-0022]] was accepted the same hour.** The delegate may now push to non-deploy remotes. Hold both decisions at once and an unauthenticated write from anything on the Wi-Fi can reach a remote. Neither ADR sees that alone; it exists only in the pair, which is the argument for deciding them against each other rather than in sequence.

### Why not simply keep option 3

Because option 3 makes the difference **permanent and principled** — *"the difference is a property of the surface"* — and Edwin's goal is real: the same functionality across surfaces is worth having, and this note had quietly converted "we have not built authentication" into "the browser must never write". Those are different claims, and only the first is true.

Option 4 keeps every guard option 3 keeps, and stops calling the gap a principle.

Consequences:

1. **It gets the Overview**, now. The overview is pure read, it answers "where does this project stand", and it is the single most useful thing to have on a tablet. Nothing about it waits on authentication.
2. **It gets the Design register and artifacts, read-only**, now. Framing a design artifact is reading. The *verdict* controls wait with every other actuator.
3. **Every actuator stays mode-3 until [[REQ-0034]] is implemented** — no transition, tick, capture, verdict or test run is reachable from the browser surface, enforced server-side exactly as it is today. [[REQ-0027]] is **unweakened by this decision**, and nothing here is licence to drop `_require_loopback` from a handler.
4. **[[REQ-0034]] is the unlock, and it gates [[PHASE-029]].** A write from a non-loopback surface must carry proof of who is asking. When it exists, the loopback check is *replaced* by that proof rather than deleted, and parity arrives for every verb at once rather than one endpoint at a time.
5. **The view set is declared once** and both renderers consume it, with each view marked as reading or actuating. A new view must be classified to exist; that is what stops the next silent divergence. Under option 4 the classification also says *what it waits on*, so "absent" and "absent for now" stop looking the same.
6. **[[RISK-0005]] re-opens when [[REQ-0034]] lands.** It closed on the strength of a mitigation — loopback-only, enumerated by walking the route table, driven over a real LAN interface — that this decision plans to replace. A risk whose mitigation is being swapped is a live risk again, and its own trigger already says so: *"any proposal to let mode 1 write."*

## Consequences

- `Recent`'s two verdicts resolve by the same rule: it is a reading view, so if it earns a place it earns it in both, and if it does not it goes from both. It cannot stay live in one and retired in the other.
- The shell keeps views the browser lacks **for now**, and the note says which and why — a stated stage rather than either a backlog item or a permanent property.
- This decision does not itself widen any surface. [[REQ-0032]] and [[PHASE-029]]'s exit criteria carry the guard, and [[RISK-0001]] is re-scanned before the phase closes.

## Acceptance

**Its own open threads, as criteria** ([[FEAT-0096]]). This decision is not a yes/no: it proposes Option 3 and leaves two things unsettled inside its own consequences. Each can be answered on its own, with evidence, from the note page — and accepting the ADR with either still open is allowed, because a person may take a decision while a thread stands and the record should show that rather than prevent it.

- [x] **The read-only digest of what is owed:** consequence 3 deferred it to an authenticated path rather than deciding it. — **decided by option 4**: it is not a special case at all. The digest is one of the things parity delivers, and it arrives with [[REQ-0034]] like every other verb rather than being smuggled in ahead of them. — evidence: this ADR's option 4 and its consequence 4 (user:edwin, 2026-08-12)
- [ ] **`Recent`'s two verdicts:** the consequences resolve it *"by the same rule"* — a reading view lives in both surfaces or neither — without saying which it is. Say which.

## Status

`accepted` — **option 4**, 2026-08-12. [[PHASE-029]] is unblocked and its shape is now known: it inherits [[REQ-0034]] as a precondition rather than a hole to discover mid-flight.

*Updated 2026-08-12: the two criteria above are why this sat undecided. `Accept` stamped five consequences and both open threads in one click, and there was nowhere to say "yes to option 3, but not consequence 3 as written" ([[ISS-0152]]). Now there is — each thread is answerable on its own, and the verb itself can carry a sentence.*

## Decision record

> [!note] Accept — option 2: Full parity — 2026-08-12 (user:edwin)
> Recorded in the app, then reconsidered in the same session. Kept because a decision record that erases its own first answer is not one — and because this is the pair of clicks that found the compounding with ADR-0022.

> [!note] Accept — option 4: Parity, gated on an authenticated write path — 2026-08-12 (user:edwin)
> *"I am thinking now that we should go for full parity because we want to be able to support the same functionality across multiple surfaces (a feature very much promoted for the t3.codes app), not sure how much of a concern the security issues raised are when used within very clear boundaries. But open for push back."*
>
> The pushback: the loopback check is the entire authorisation model, a LAN is a boundary a router advertises rather than one the OS enforces, one of these repos publishes a live website, and ADR-0022 — accepted the same hour — lets the delegate push. Parity is the right goal; authentication is what makes it safe rather than an obstacle to it.
>
> Agreed, and option 4 is the result.
