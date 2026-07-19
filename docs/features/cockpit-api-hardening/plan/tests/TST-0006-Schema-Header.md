---
type: "[[test]]"
id: TST-0006
aliases: ["TST-0006"]
title: "Every JSON endpoint emits X-Cockpit-Schema matching cockpit.SCHEMA_VERSION"
status: passing
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: ["[[TASK-0068]]"]
verifies: ["[[TASK-0068]]", "[[FEAT-0008-Cockpit-API-Hardening]]"]
path: "tests/test_schema_header.py"
---

# TST-0006 — `X-Cockpit-Schema` header coverage

## Intent
Schema drift between server and client is the failure mode the
versioning rule (documented in `docs/references/COCKPIT-API.md`)
exists to make loud. This test is the gate.

A parameterised pytest case walks every JSON endpoint listed in the
contract doc — `healthz`, the four `/api/cockpit/*` endpoints, the
new `/api/render`, both POST endpoints, plus a handful of error
responses (400 / 403 / 404) — and asserts:

1. `X-Cockpit-Schema` is present on every response.
2. Its value equals `str(cockpit.SCHEMA_VERSION)`.
3. `/healthz`'s body `schema` field agrees with the header on the
   same response.

Error responses are included on purpose: the renderer's first
parse step is the schema check, so a 4xx response without the
header would mean the renderer can't even surface the error
cleanly.

## Location
`tests/test_schema_header.py` — 17 parametrised cases + 1 healthz
body-vs-header agreement check. All passing as of 2026-05-25
(`pytest tests/test_schema_header.py -v`).

## What this catches
- A new endpoint added with a hand-rolled response writer that
  bypasses `_respond_json` and forgets the header.
- A bump to `SCHEMA_VERSION` without updating the cached client
  constants (the bump itself doesn't break this test, but the
  paired client-side test would).
- A regression that strips headers on the error path.

## Status
`passing` — 17/17.
