---
type: security
id: SECURITY
status: active
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
tags: [security]
---

# Security

## Threat model

`docs-server` runs locally and serves a project-os repo's `docs/` tree as HTML. Two surfaces:

1. **Render endpoint** — read-only HTTP. Intended to be reachable from devices on the same Wi-Fi (e.g. a tablet) for browsing the docs.
2. **Terminal endpoint** *(optional, off by default)* — wraps a shell or AI coding assistant. Anyone who can reach this URL can run shell commands as the user running `docs-server`.

## Bindings (MUST)

- The render endpoint binds to `0.0.0.0` by default. Acceptable because it serves only files inside the configured `docs/` directory.
- The terminal endpoint MUST bind to `127.0.0.1` only. Cross-network exposure of the terminal is a privilege-escalation foothold and is explicitly out of scope. The default-off state and the bind constraint together make this hard to misconfigure. See `docs/risks/RISK-0001-Terminal-Exposure.md`.

## Path traversal

The render endpoint MUST refuse to serve paths outside the configured `docs/` root. Realpath-resolution + parent-prefix check is the standard guard.

## Reporting

Local tool, single-user. Report issues via the project-os system as `ISS-*` notes; if the issue is exploitable across users sharing a tablet/network, mark `severity: high` and prioritise.
