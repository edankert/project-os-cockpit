---
type: "[[test]]"
id: TST-0004
aliases: ["TST-0004"]
title: "Sidecar contract — /healthz, COCKPIT_DESKTOP gating, mode-1 regression guard"
status: passing
phase: "[[PHASE-005-Desktop-Shell]]"
owner: user:edwin
created: 2026-05-24
updated: 2026-05-24
source: ["[[TASK-0059]]"]
verifies: ["[[TASK-0059]]", "[[FEAT-0007]]"]
path: "tests/test_sidecar_contract.py"
---

# TST-0004 — Sidecar contract

## Intent
Verifies the three additive surface points the Electron desktop shell
(FEAT-0007) depends on, **and** that the per-project browser mode
(mode 1) is unaffected.

Coverage:

1. **`_desktop_mode()` gate.** Only the exact value `COCKPIT_DESKTOP=1`
   activates desktop mode. Other truthy strings (`"true"`, `"yes"`,
   `""`) do not — protects against accidental activation when the env
   var leaks in from an unrelated context.
2. **`GET /healthz` identity payload.** Returns `200` with
   `{ok, service, schema, docs_root, desktop_mode}`. The shell uses
   `service` to refuse to attach to an unrelated process bound to the
   same port; uses `desktop_mode` to confirm the sidecar was spawned
   with the right env.
3. **Terminal short-circuit.** In desktop mode `TerminalProcess.is_available()`
   returns `False` even when ttyd is on PATH, and `info()` returns a
   reason that mentions "desktop" rather than the misleading
   `brew install ttyd` install hint.
4. **Mode-1 regression guard.** With no env var set, terminal `info()`
   still returns the canonical "ttyd binary not found" hint when ttyd
   is absent — proves the new code path doesn't shadow the old one.
5. **Discovery-file gate.** `_write_discovery_file` writes `.cockpit/url`
   in mode 1 and is skipped in desktop mode. Tested via the same
   conditional the server uses inside `DocsServer.run()`.

## Location
`tests/test_sidecar_contract.py` — 10 tests, all passing as of
2026-05-24. Uses pytest's `monkeypatch.setenv` / `delenv` to flip the
env var without polluting global state, and the same
`_NoDNSThreadingHTTPServer` ephemeral-port pattern as TST-0003 for the
HTTP probes.

## Status
`passing` — 10/10 (`pytest tests/test_sidecar_contract.py -v`).
