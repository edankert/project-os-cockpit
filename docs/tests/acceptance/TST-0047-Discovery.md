---
type: "[[test]]"
id: TST-0047
aliases: ["TST-0047"]
title: "Discovery"
status: active
owner: user:edwin
created: 2026-08-17
updated: 2026-08-17
tier: 1
area: "Desktop shell and workspaces"
covers: ["[[FEAT-0007]]", "[[FEAT-0009]]", "[[FEAT-0016]]"]
related: []
level: acceptance
---

# Discovery

launch the shell with no arguments. Expect: every `SNAPSHOT.yaml`-bearing repo under `~/Dev/repos/` appears in the rail, each with its own sidecar. — 2026-08-10, live shell over CDP: **10** rail squares, each carrying its validator verdict and remote state (`no remote — nothing is backed up` on `articles`; `34 commits not pushed (remote is a deploy target)` on `your-applications.com`).
