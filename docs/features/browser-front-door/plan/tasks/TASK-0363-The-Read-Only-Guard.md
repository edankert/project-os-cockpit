---
type: "[[task]]"
id: TASK-0363
aliases: ["TASK-0363"]
title: "A test asserts every actuating endpoint refuses a non-loopback peer, and fails when a new one forgets"
status: backlog
phase: "[[PHASE-029-One-Tool-Two-Front-Doors]]"
owner: user:edwin
created: 2026-08-09
updated: 2026-08-09
source: ["[[REQ-0032-Two-Front-Doors-Agree-Or-Differ-On-The-Record]]", "[[RISK-0001-Render-Server-Exposure]]"]
parent: "[[FEAT-0083-The-Browser-Cockpit-Answers-Questions]]"
effort: S
due: ""
depends: []
blocks: ["[[TASK-0361-The-Overview-On-The-Reading-Surface]]", "[[TASK-0362-The-Design-Register-Read-Only]]"]
related: []
tests: []
---

# The read-only guard

## Definition of Done
- [ ] Every write endpoint is enumerated from one place and asserted to refuse a non-loopback peer
- [ ] Adding a write endpoint without the check fails the test — enumerated, not hand-listed
- [ ] The test states the threat model it guards in one sentence, naming [[RISK-0001]]

## Steps
- [ ] Enumerate the POST routes from `server.py`'s dispatch rather than restating them, so a new route joins the suite by existing
- [ ] Assert refusal with a simulated non-loopback peer address
- [ ] Cross-check against `note_writes`' documented callers

## Notes
**This lands before the two porting tasks, not after.** It is the guard that makes widening the reading surface safe, and a guard written after the widening has already been trusted once.

The measured hazard is specific: mode 1 is served on `0.0.0.0` so a tablet can read, and the only thing separating reading from writing is a per-request peer check on the shared socket. That check is correct today. Nothing currently fails if someone adds an endpoint and omits it.
