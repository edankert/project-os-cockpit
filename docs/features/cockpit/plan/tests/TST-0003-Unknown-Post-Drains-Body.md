---
type: "[[test]]"
id: TST-0003
aliases: ["TST-0003"]
title: "Unknown POST drains body — keep-alive stays synced"
status: passing
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-23
updated: 2026-05-23
source: ["[[TASK-0057]]"]
verifies: ["[[TASK-0057]]", "[[FEAT-0006]]"]
path: "tests/test_cockpit_state.py::test_unknown_post_drains_body_to_keep_connection_synced"
---

# TST-0003 — Unknown POST drains body

## Intent
Pipelines two HTTP requests on one keep-alive TCP socket — a `POST /api/cockpit/does-not-exist` with a JSON body, then a `GET /_static/cockpit.css`. The fix passes when the second response is `200 OK` (CSS bytes) rather than `501 Unsupported method` (which is what an undrained body produces).

## Why this matters
Prior to TASK-0057, the cockpit could be put into an unstyled state simply by sending a POST to an unknown route — the kind of thing the JS does naturally when client and server are at different versions. Hard to debug because the symptom (CSS missing) is far from the cause (undrained POST).

## Location
`tests/test_cockpit_state.py::test_unknown_post_drains_body_to_keep_connection_synced` — uses a real `ThreadingHTTPServer` on an ephemeral port; raw socket sends the pipelined request, asserts both responses come back, asserts the second is 200 and the phrase `Unsupported method` is absent from the wire bytes.

## Status
`passing`
