---
type: "[[test]]"
id: TST-0017
aliases: ["TST-0017"]
title: "Sidecar identity guard — foreign-cwd rejection, identity endpoint, external-hook fallback"
status: passing
kind: automated
owner: user:edwin
created: 2026-07-19
updated: 2026-07-19
validates: ["[[TASK-0146]]", "[[ISS-0007]]"]
related: ["[[TST-0015]]"]
---

# TST-0017 — sidecar identity guard

Automated pytest coverage (`tests/test_identity_guard.py`) against a live `_NoDNSThreadingHTTPServer`:

1. `POST /api/agent-hook` with `cwd` inside the served project root → 200, tracker ingests.
2. Same POST with `cwd` in a *different* repo → 409, tracker session index unchanged, no agent-state written.
3. `cwd` in a subdirectory of the root and with case-mangled path → accepted (case-normalised containment, ISS-0001 lesson).
4. Payload without `cwd` → accepted (statusline/forwarder compatibility).
5. `GET /api/cockpit/identity` → `{root, docs_root, pid}` matching the served tree.
6. End-to-end ISS-0007 replay: the embedded external-hook script (extracted from `app-settings.ts`, as in TST-0015) posts to a *wrong* repo's sidecar via a stale url file → server rejects → hook falls back to writing `agent-state.json` in the correct repo; the wrong sidecar's tracker stays clean.
