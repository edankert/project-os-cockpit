---
type: "[[risk]]"
id: RISK-0001
aliases: ["RISK-0001"]
title: "Terminal endpoint accidentally bound to non-loopback interface"
status: open
severity: high
likelihood: low
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
related: ["[[FEAT-0003]]", "[[REQ-0005]]"]
---

# RISK-0001 — Terminal exposure

## Hazard
The embedded terminal endpoint exposes shell access. If misconfigured to bind to `0.0.0.0` (or any interface other than `127.0.0.1`), anyone reachable on that interface can run shell commands as the user running project-os-cockpit. This is a privilege-escalation foothold for any device on the LAN.

## Likelihood
Low — the default is loopback-only, the feature is off by default, and binding it elsewhere requires deliberate flag changes.

## Severity
High — successful exploitation gives full shell access to the user account. On a developer machine this typically means access to source code, SSH keys, and cloud credentials.

## Mitigations
- Default-off: the terminal feature requires explicit `--terminal` opt-in.
- Default-loopback: even when enabled, the bind defaults to `127.0.0.1`.
- Validation: the CLI rejects `--terminal-bind` values that aren't loopback (`127.0.0.1`, `::1`, `localhost`); to override requires an explicit `--terminal-allow-non-loopback` escape hatch.
- Documented in `SECURITY.md` and `docs/decisions/ADR-0002-Terminal-Approach.md`.
- Rendered template omits the iframe for non-loopback HTTP clients, so the affordance simply doesn't exist on the tablet.

## Residual risk
With the mitigations above, the risk reduces to user error (deliberately disabling the loopback default and the validation). At that point it's an informed choice.
