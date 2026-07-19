---
type: "[[risk]]"
id: RISK-0003
aliases: ["RISK-0003"]
title: "Python 3.11+ runtime requirement excludes default macOS / common LTS"
status: open
severity: low
likelihood: medium
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
related: ["[[FEAT-0001]]", "[[FEAT-0005]]", "[[CHG-20260507-Bootstrap-Python-Project]]"]
---

# RISK-0003 — Python 3.11+ runtime floor

## Hazard
`pyproject.toml` declares `requires-python = ">=3.11"`. macOS still ships 3.9 in `/usr/bin/python3`, and several Linux LTS distros (Debian 11, Ubuntu 20.04) ship 3.8/3.9 by default. Anyone trying to run `project-os-cockpit` against the system interpreter will see an opaque dependency-resolution failure rather than a clear "wrong Python" message.

## Likelihood
Medium — the very first dev environment for this project hit it (system Python 3.9.6); we needed `brew install python@3.13`. Same will happen for any teammate or CI image without an explicit Python install.

## Severity
Low — the failure mode is a confusing error at install time, not silent corruption or data loss. The fix is well-known: install a newer Python.

## Mitigations
- README documents the 3.11+ floor (already present).
- The downstream-pilot shim (FEAT-0005) should explicitly require/check for a 3.11+ interpreter before invoking the server, so consumers don't hit the issue inside the shim.
- When CI gets added, the workflow should pin to a 3.11+ image rather than relying on the runner default.
- Consider relaxing the floor to 3.10 if a real consumer hits the constraint and 3.10 is sufficient (most stdlib features used so far are pre-3.11).

## Residual risk
Newcomers will still occasionally trip on it. Acceptable — better than silently degrading on older Python versions.
