---
type: "[[phase]]"
id: PHASE-029
aliases: ["PHASE-029"]
title: "One tool, two front doors — the browser cockpit and the desktop shell answer the same questions, and differ only where a difference was decided"
status: planned
order: 29
owner: user:edwin
created: 2026-08-09
updated: "2026-08-20"
goal: "Make the browser cockpit a deliberate subset of the same tool rather than an older version of it: one view vocabulary, the question-answering surfaces reachable from both, and every remaining difference traceable to a recorded decision about what the read-only front door is for."
features:
  - "[[FEAT-0083-The-Browser-Cockpit-Answers-Questions]]"
  - "[[FEAT-0084-One-View-Vocabulary]]"
requirements:
  - "[[REQ-0032-Two-Front-Doors-Agree-Or-Differ-On-The-Record]]"
  - "[[REQ-0034]]"
issues: ["[[ISS-0246-The-Two-Front-Doors-Are-Not-Comparable]]"]
depends: ["[[PHASE-023-Levers-For-The-Human]]"]
related: ["[[ADR-0010-What-The-Browser-Cockpit-Is-For]]", "[[REQ-0027]]", "[[RISK-0005]]", "[[REQ-0013-Cockpit-Three-Pane-Layout]]", "[[RISK-0001-Render-Server-Exposure]]"]
tags: [surfaces, mode-1]
---

# One tool, two front doors

## Scoped 2026-08-20 — what parity actually costs, measured

Edwin confirmed **parity** when asked on 2026-08-20, which is [[ADR-0010]]'s existing decision (option 4, accepted 2026-08-12) rather than a new one. This phase has been `planned` and unscoped since; the measurement below is what it is planned *for*.

**Virtual pages implemented in each front door:**

| front door | count | pages |
|---|---|---|
| `desktop/src/renderer/renderer.ts` | **12** | `~agents` `~checks` `~design` `~features` `~history` `~inbox` `~issues` `~overview` `~publication` `~release` `~review` `~tests` |
| `src/project_os_cockpit/static/cockpit.js` | **2** | `~note` `~root` |

The browser cockpit renders **notes and a navigator**. Every view the tool has been about is in the desktop shell alone.

### The eleven that are owed NOW

[[ADR-0010]] gates *writes* on authentication, not reads. These answer a question without changing anything, so nothing blocks them:

`~overview` · `~features` · `~issues` · `~tests` · `~checks` · `~design` · `~history` · `~agents` · `~inbox` · `~publication` · `~review`

### The one that is gated, and why the gate is real

`~release` carries `Mark released`, the seal, and now the contents picker ([[TASK-0511]]/[[TASK-0558]]). [[ADR-0010]]: *"The loopback check is not a safety feature on top of an authorisation model. It **is** the authorisation model."* [[REL-0001]]'s acceptance pass drove every mutation endpoint over the real LAN interface — **ten of ten returned 403 while reads returned 200** ([[REQ-0027]], [[RISK-0005]]).

So the order is: the eleven reading views, then an authenticated write path, then the writing surfaces. Not the other way round, and not all at once.

### What this phase must stop happening

*Both front doors* has been quoted at pairs where only one side has the surface — [[TASK-0511]] deferred its picker as a small follow-up when the page does not exist there and, under the ADR, could not carry a write even if it did. Each deferral reads as an omission rather than as a precondition nobody has met. That is [[ISS-0246]].



## Where this came from

A review of every nav mode on 2026-08-09 (session with Edwin) measured the two surfaces side by side:

| | views exposed |
|---|---|
| **Mode 3** (desktop shell) | Overview · Design · Features · Tasks · Issues · Review · Library |
| **Mode 1** (browser, `0.0.0.0`) | Project · Features · Tasks · Issues · Recent |

The browser has **none of the three views that answer a question** — Overview, Design, Review. It has three list navigators and `Recent`, which mode 3 classifies as retired. The render server binds `0.0.0.0` *specifically so a tablet on the same Wi-Fi can read the notes*, and what the tablet gets is the 2026-05 tool.

`recent` is the sharpest instance: one view with two verdicts — a live button in `cockpit.js`, a member of `RETIRED_NAV_MODES` in `renderer.ts`. Nothing reconciles them, and nothing would notice.

## The goal is not parity

Parity is the wrong target and this phase says so up front. The browser surface is reachable from the LAN and must stay read-only ([[RISK-0001]]); the desk performs writes, and those endpoints refuse non-loopback callers by design. So the Review desk cannot simply appear in mode 1, and "make them the same" would be a security regression wearing a UX justification.

What the phase asks for is weaker and more useful: **the difference is decided rather than inherited.** [[ADR-0010]] decides what the browser front door is *for*; everything else follows from it.

## Scope

[[ADR-0010]] first — it gates both features. [[FEAT-0083]] brings the question-answering surfaces that are safe to bring. [[FEAT-0084]] makes the view vocabulary single-sourced so the next divergence cannot happen silently, and resolves `recent`'s two verdicts.

## Exit criteria

- [ ] [[ADR-0010]] is accepted, and states what the browser cockpit is for in a sentence someone can disagree with
- [ ] Every view present in one front door and absent from the other is absent *because ADR-0010 says so*, and the reason is readable from the code
- [ ] The view set is declared once and consumed by both renderers; adding a view to one without deciding about the other is not possible without the guard failing
- [ ] `recent` has one verdict
- [ ] No write path becomes reachable from a non-loopback peer — re-scanned against [[RISK-0001]] before the phase closes

## Deferred deliberately

Opened `planned`, not `active`. Edwin's direction on 2026-08-09 was to align the browser view **at a later stage**; this phase exists so the finding is not lost and the work has a home, not because it is next.

## Unblocked, and reshaped — 2026-08-12

The gate is decided: [[ADR-0010]] took **option 4** — parity across surfaces, gated on an authenticated write path.

**What that changes about this phase.** It was waiting on a decision that could have gone three ways, two of which would have shrunk it. It now has a known shape and one precondition it did not have before:

- **[[REQ-0034]] joins the phase** and gates every actuating surface in it. A write from a non-loopback peer must prove who is asking; until that exists, mode 1 gains reading views only.
- **The reading half can proceed immediately** — the overview and the design register, read-only, wait on nothing.
- **[[RISK-0005]] re-opens before REQ-0034 is implemented**, and the phase does not close over a risk left closed on a mitigation it replaced.
- **The view set is classified** as reading or actuating, and an actuating view absent from mode 1 now says *what it waits on* — "absent" and "absent for now" stopped meaning the same thing.

**The trap this avoids** is the one the decision was reconsidered to avoid: starting the parity work, meeting the loopback check halfway through, and deleting it because it is in the way. The precondition is a phase member now, so it is scheduled rather than discovered.

## The precondition landed first — 2026-08-20

**[[TASK-0363]] is `done` while this phase stays `planned`**, and that asymmetry is deliberate rather than drift.

The section above names the trap: *"starting the parity work, meeting the loopback check halfway through, and deleting it because it is in the way."* The guard is the one piece of this phase that is worth having **before** the phase opens, because its whole value is being in place before anyone is inconvenienced by it. [[FEAT-0083]] says the same thing in stronger words — *"a guard written after the widening has already been trusted once."*

So it was built and nothing else was. The phase status is **not** flipped to `active`: Edwin's direction on 2026-08-09 was to align the browser at a later stage, that direction has not changed, and a phase that reads `active` because one preparatory task closed would misreport what is being worked. `PHASE-037` is the active phase; this one gained a finished precondition, not a start date.

**What the reader should take from the mismatch.** One `done` task under a `planned` phase means exactly what it looks like: the gate is ready and the work behind it has not begun. When this phase does open, the first two porting tasks ([[TASK-0361]], [[TASK-0362]]) are already unblocked — `blocks:` on TASK-0363 lists them both, and it is now satisfied.

**What did not land, and is not implied by this.** [[REQ-0034]] — the authenticated write path — is untouched. The guard proves the current authorisation model *works*; it does not replace it, and every actuating view still waits on REQ-0034 exactly as the section above says. The eleven reading views are also untouched: the baseline is measured (`cockpit.js` fetches **two** endpoints) and pinned, so their arrival will be visible as movement in a number rather than an assertion that nothing broke.
