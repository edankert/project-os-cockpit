---
type: "[[requirement]]"
id: REQ-0006
aliases: ["REQ-0006"]
title: "Render endpoint binds to 0.0.0.0 (LAN read access)"
status: verified
phase: "[[PHASE-001-MVP]]"
implements: ["[[FEAT-0001]]"]
owner: user:edwin
created: 2026-05-07
updated: 2026-05-23
implemented_by: ["[[FEAT-0001]]"]
verified_by: []
---

# REQ-0006 — Render endpoint LAN access

The render endpoint SHALL bind to `0.0.0.0` by default so devices on the same LAN (a tablet, a phone) can read the rendered docs over Wi-Fi.

The endpoint SHALL be read-only — no editing, no shell access, no file write — so LAN exposure is acceptable.

The bind address SHALL be configurable via a CLI flag (`--bind`) for the rare case the user wants to lock to loopback.

## Rationale
Reading docs on a second device while editing on the primary is a real workflow. The whole tablet-as-secondary-screen pattern is one of the headline use-cases of this tool.

## Verification
- 2026-05-23: marked `verified` — Render server binds to 0.0.0.0 per CLI default; LAN access proven via downstream pilot.
