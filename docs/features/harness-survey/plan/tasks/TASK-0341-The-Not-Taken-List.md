---
type: "[[task]]"
id: TASK-0341
aliases: ["TASK-0341"]
title: "The not-taken list — every declined capability with the reason, so the same idea is not re-litigated each round"
status: backlog
phase: "[[PHASE-028-Borrowed-Capability]]"
owner: user:edwin
created: 2026-08-05
updated: 2026-08-13
source: ["[[FEAT-0080-The-Harness-Survey]]"]
parent: "[[FEAT-0080-The-Harness-Survey]]"
effort: S
depends: []
blocks: []
related: ["[[TASK-0414-The-Remote-Transport-Round]]"]
tests: []
---

# The not-taken list

## Definition of Done

- A reference note listing declined capabilities, each with the tool it came from, the reason, and the condition that would reopen it — a decline is a decision with a shelf life, not a verdict for all time.
- Seeded from the first round's explicit declines: multi-forge source control (`gh` suffices; FEAT-0055's deploy-remote refusal is worth more than breadth), Effect-TS event-sourced orchestration (scale mismatch), a general editor or conversation UI (not the thesis), hosted relay tunnels (a service, not a feature).
- Referenced by the survey skill so the next round starts by reading it.

## Declines from round 3 — the remote-transport round ([[TASK-0414-The-Remote-Transport-Round]], 2026-08-13)

- **A pairing token exchanged for a long-lived session** (t3.code: `t3 pair`, `t3 auth`). *Reason:* [[REQ-0034]] rejected this shape before the survey saw it — *"a surface that authenticates once and then writes freely is a session, and a session on a shared network is a shared session."* The proof must be per-request. *Reopens if:* we adopt a phone/browser surface where per-request proof is impractical, in which case the requirement is what changes, deliberately and in writing.
- **Hosted relay tunnels** (t3's T3 Connect, VS Code dev tunnels). *Reason:* already declined in round 1 — a service, not a feature — and PHASE-033 rejected a cloud relay independently. Recorded again because both surveyed tools lead with it, so it will keep arriving. *Reopens if:* someone needs access from a network SSH cannot cross, which nothing has yet asked for.
- **Adopting AHP (the VS Code Agent Host protocol) as our protocol.** *Reason:* it is a good protocol for a product that hosts agent adapters in-process; the cockpit shells out to CLIs in a PTY and reads their hooks. Adopting the protocol would mean adopting the architecture, which is round 1's "machinery because it looks architecturally impressive" decline in a new coat. **Its *shape* is a take** — snapshot plus ordered actions with replay-on-reconnect — recorded as an adapt in [[TASK-0414]]. *Reopens if:* we ever host an agent in-process rather than in a terminal.
- **Binding the backend to a LAN interface with a pairing link** (t3's option 1). *Reason:* [[REQ-0027]]/[[REQ-0034]] and [[ADR-0010]] already decide this for the browser door; the survey adds no new evidence and the fleet contains a repo whose only remote deploys a live website. *Reopens if:* [[REQ-0034]] lands, at which point it is that requirement's decision, not this list's.
