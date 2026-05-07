---
type: "[[requirement]]"
id: REQ-0005
aliases: ["REQ-0005"]
title: "Terminal endpoint binds to 127.0.0.1 only"
status: approved
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
implemented_by: ["[[FEAT-0003]]"]
verified_by: []
---

# REQ-0005 — Terminal local-only

When the embedded-terminal feature is active, the terminal endpoint SHALL bind exclusively to the loopback interface (`127.0.0.1`). It MUST NOT be reachable from any other interface.

The render server's HTML template SHALL detect non-loopback requests and omit the terminal `<iframe>` from the rendered output for those clients (so a tablet on the LAN never even sees a placeholder).

## Rationale
The terminal endpoint allows shell command execution. If reachable across the network, anyone on the LAN can run shell commands as the user running project-os-cockpit. The loopback bind is the single most important security control in this system. See [[RISK-0001]].
