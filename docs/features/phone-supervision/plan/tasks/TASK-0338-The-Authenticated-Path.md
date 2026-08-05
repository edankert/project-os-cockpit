---
type: "[[task]]"
id: TASK-0338
aliases: ["TASK-0338"]
title: "The authenticated path — bearer-paired, off by default, per-repo, and re-scanned against the write-surface risk"
status: backlog
phase: "[[PHASE-028-Borrowed-Capability]]"
owner: user:edwin
created: 2026-08-05
updated: 2026-08-05
source: ["[[FEAT-0079-Supervision-From-A-Phone]]"]
parent: "[[FEAT-0079-Supervision-From-A-Phone]]"
effort: L
depends: []
blocks: ["[[TASK-0339-The-Supervision-Payload]]"]
related: ["[[RISK-0005-The-Write-Surface]]"]
tests: []
---

# The authenticated path

## Definition of Done

- A pairing flow issues a per-device bearer credential from the desktop; unpaired requests are refused exactly as non-loopback ones are today.
- **Off by default and enabled per repo** — the blast radius of a mistake is one repo, matching the delegation policy's shape.
- The anonymous `0.0.0.0` render surface is unchanged and still read-only: this adds a path, it never relaxes the existing guard.
- [[RISK-0005]] is re-scanned and amended with this path's own failure modes before the feature closes — a new door reopens the risk that governs doors.
- The hardening suite gains the paired cases: unpaired, revoked, wrong-repo, expired.
