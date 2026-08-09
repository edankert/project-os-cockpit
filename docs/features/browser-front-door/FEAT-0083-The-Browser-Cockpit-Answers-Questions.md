---
type: "[[feature]]"
id: FEAT-0083
aliases: ["FEAT-0083"]
title: "The browser cockpit answers questions — the overview and the design register reach the reading surface, and the desk deliberately does not"
status: planned
phase: "[[PHASE-029-One-Tool-Two-Front-Doors]]"
owner: user:edwin
created: 2026-08-09
updated: 2026-08-09
source: ["[[ADR-0010-What-The-Browser-Cockpit-Is-For]]"]
goal: "Give the LAN reading surface the two read-only surfaces that answer questions — the project overview and the design register — so a tablet gets the current tool rather than the one that existed before PHASE-008."
requirements: ["[[REQ-0032-Two-Front-Doors-Agree-Or-Differ-On-The-Record]]"]
tasks:
  - "[[TASK-0361-The-Overview-On-The-Reading-Surface]]"
  - "[[TASK-0362-The-Design-Register-Read-Only]]"
  - "[[TASK-0363-The-Read-Only-Guard]]"
release: ""
related: ["[[PHASE-029-One-Tool-Two-Front-Doors]]", "[[RISK-0001-Render-Server-Exposure]]", "[[FEAT-0040-Overview-Rework]]", "[[FEAT-0079-Supervision-From-A-Phone]]"]
tests: []
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
