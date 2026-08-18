---
type: "[[feature]]"
id: FEAT-0079
aliases: ["FEAT-0079"]
title: "Supervision from a phone — the digest, the queue and a few approvals over one authenticated path, without widening the read surface into a write surface"
status: planned
phase: "[[PHASE-028-Borrowed-Capability]]"
owner: user:edwin
created: 2026-08-05
updated: 2026-08-05
source: ["Comparison against t3.codes, 2026-08-05: direct, bearer-paired, relay-tunnelled, Tailscale and SSH access to one runtime boundary — 'remoteness is expressed at the connection layer, never by splitting the runtime'"]
goal: "One authenticated remote path carrying exactly what supervision needs — the since-you-looked digest, the desk queue, and the principal's approvals — so a delegated worker can be watched from away without the LAN render surface ever gaining a write."
requirements: []
tasks:
  - "[[TASK-0338-The-Authenticated-Path]]"
  - "[[TASK-0339-The-Supervision-Payload]]"
release: ""
related: ["[[FEAT-0071-Since-You-Looked]]", "[[FEAT-0060-Transitions-And-Ticks-On-The-Note]]", "[[RISK-0005-The-Write-Surface]]"]

---

# Supervision from a phone

## Goal

Under [[PHASE-027]] autonomy, supervision **is** reading plus a handful of approvals — a phone-sized job. [[FEAT-0071]]'s digest and [[FEAT-0060]]'s actuators are already the payload; what is missing is a way to reach them from away.

## The line this must not cross

The render server binds `0.0.0.0` so a tablet can *read*, and [[RISK-0005]] exists because every mutation endpoint added there is one a device on the Wi-Fi could reach. The loopback check is the whole guard.

So remote supervision is **not** "relax the loopback rule". It is a second, authenticated path — bearer-paired, off by default, per-repo — carrying a deliberately narrow payload. T3's model is instructive precisely here: one runtime boundary, remoteness at the connection layer, never a second runtime with second rules.

## Out of Scope

- **A phone client.** A responsive web surface over the authenticated path first; native apps are a different project with app-store consequences.
- **Terminal access from away.** Watching and approving, not driving. The terminal endpoint's second bind stays Mac-local.
- **Tunnels and relays.** Tailscale or the LAN is enough for one human; a hosted relay is a service, not a feature.
