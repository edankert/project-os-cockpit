---
type: "[[feature]]"
id: FEAT-0083
aliases: ["FEAT-0083"]
title: "The browser cockpit answers questions — the overview and the design register reach the reading surface, and the desk deliberately does not"
status: planned
phase: "[[PHASE-029-One-Tool-Two-Front-Doors]]"
owner: user:edwin
created: 2026-08-09
updated: "2026-08-20"
source: ["[[ADR-0010-What-The-Browser-Cockpit-Is-For]]"]
goal: "Give the LAN reading surface the two read-only surfaces that answer questions — the project overview and the design register — so a tablet gets the current tool rather than the one that existed before PHASE-008."
requirements: ["[[REQ-0032-Two-Front-Doors-Agree-Or-Differ-On-The-Record]]"]
tasks:
  - "[[TASK-0361-The-Overview-On-The-Reading-Surface]]"
  - "[[TASK-0362-The-Design-Register-Read-Only]]"
  - "[[TASK-0363-The-Read-Only-Guard]]"
release: ""
related: ["[[PHASE-029-One-Tool-Two-Front-Doors]]", "[[RISK-0001-Render-Server-Exposure]]", "[[FEAT-0040-Overview-Rework]]", "[[FEAT-0079-Supervision-From-A-Phone]]"]

---

# The browser cockpit answers questions

## Goal

Mode 1 has no Overview, no Design and no Review. Two of those three are pure reads and belong on the reading surface; the third does not, and saying so is part of the work.

`/api/cockpit/stats` already serves the overview payload and mode 1 already consumes several cockpit APIs, so this is renderer work against endpoints that exist, not new server capability.

## Scope

**In:**

- The project overview in `cockpit.js`, including the phase accordion and the scope rows — the same payload the shell renders
- The design register and read-only artifact framing
- A test that fails if any actuating endpoint becomes reachable from a non-loopback peer

**Out:**

- **The review desk.** Per [[ADR-0010]]: its endpoints refuse non-loopback callers, and a queue of obligations you cannot discharge is worse than no queue. A read-only *digest* of what is owed belongs to [[FEAT-0079]]'s authenticated path, which is designed for it.
- **Every verdict, tick, capture and test-run control.** Reading a design is reading; judging it is not.
- **Feature parity as a goal.** [[ADR-0010]] chose subset-by-classification over parity.

## Acceptance

- [ ] Mode 1 exposes the project overview, rendering the same `/api/cockpit/stats` payload as the shell, with phases and scope rows
- [ ] Mode 1 exposes the design register and can frame an artifact, with no verdict or capture control present in the DOM
- [ ] A test asserts that every actuating endpoint refuses a non-loopback peer, and it fails if a new one is added without that check
- [ ] Nothing in mode 1 issues a POST to a `note_writes`-backed endpoint
- [ ] [[RISK-0001]] is re-scanned and updated with what this changed

## Links

- Decision: [[ADR-0010-What-The-Browser-Cockpit-Is-For]] — gates this feature; nothing starts until it is accepted
- Requirements: [[REQ-0032-Two-Front-Doors-Agree-Or-Differ-On-The-Record]]
- Paths: `src/project_os_cockpit/static/cockpit.js`, `src/project_os_cockpit/static/cockpit.css`, `src/project_os_cockpit/server.py`

## Widened 2026-08-20 — two of eleven, measured

This feature plans the **overview** and the **design register**. Measured while closing [[TASK-0511]], the gap is larger than two:

| front door | virtual pages |
|---|---|
| `desktop/src/renderer/renderer.ts` | **12** — `~agents` `~checks` `~design` `~features` `~history` `~inbox` `~issues` `~overview` `~publication` `~release` `~review` `~tests` |
| `src/project_os_cockpit/static/cockpit.js` | **2** — `~note` `~root` |

[[ADR-0010]] is `accepted` on **option 4 — parity gated on an authenticated write path**, decided 2026-08-12, and Edwin confirmed parity again on 2026-08-20. So the eleven **reading** views are owed and nothing gates them; `~release` is the twelfth and is gated.

### The eleven, and the order

`~overview` and `~design` already have tasks ([[TASK-0361]], [[TASK-0362]]) and are the right first two: the overview is where a reader lands, and the design register is the one this phase just gave a new group ([[TASK-0516]]).

The other nine, unplanned until now:

`~features` · `~issues` · `~tests` · `~checks` · `~history` · `~publication` · `~review` · `~agents` · `~inbox`

**Deliberately not nine task notes yet.** Each would say *"port view X"* and nothing else, and a task note per view is the thin-note proliferation [[ISS-0077]] warns about — they get minted as work starts, when there is something to say about each. What is recorded here is the **scope**, which is what [[ISS-0246]] asked for and what `planned` was missing.

### The one thing that is not a port

`~checks` and `~review` **carry write paths** on the desktop side — marking a check, recording a verdict. The reading half is owed now; the acting half joins `~release` behind the authenticated write path. Splitting them at the view boundary rather than porting whole is the difference between this being eleven reads and eleven reads plus three writes nobody authorised.

### Why the loopback check is not a detail to route around

[[REL-0001]]'s acceptance pass drove every mutation endpoint over the real LAN interface: **ten of ten returned 403 while reads returned 200** ([[REQ-0027]], [[RISK-0005]]). [[ADR-0010]]: *"The loopback check is not a safety feature on top of an authorisation model. It **is** the authorisation model."* There is no authentication anywhere in this tool.
