---
type: "[[test]]"
id: TST-0063
aliases: ["TST-0063", "CHK-0020"]
title: "Loopback only"
status: active
owner: user:edwin
created: 2026-08-17
updated: 2026-08-17
tier: 1
area: "The embedded terminal"
section: "1.9"
ordinal: 20
covers: ["[[FEAT-0003]]", "[[FEAT-0037]]"]
burden: []
migrated_from: "tests/ACCEPTANCE_TESTS.md#1.9.2 @ 7de1a86"
related: []
level: acceptance
merged_from: "CHK-0020 @ 4c02731"
---

# Loopback only

confirm the terminal endpoint refuses a connection from another device on the network. — 2026-08-10, against the running shell's own sidecar: `GET /api/terminal` returns **200 on loopback** and is **unreachable from `192.168.68.123`** (connection refused). Two mechanisms, both source-confirmed: the shell spawns its sidecar `--bind 127.0.0.1`, and `ttyd` itself is spawned `-i 127.0.0.1` — *"bind to loopback only — enforces REQ-0005 even…"*. **Residual, named rather than glossed:** the proxy path was not exercised from a non-loopback peer against a sidecar started with `--bind 0.0.0.0`; ttyd's own bind should still refuse it, but that configuration was not driven.
