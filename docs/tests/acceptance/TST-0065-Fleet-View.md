---
type: "[[test]]"
id: TST-0065
aliases: ["TST-0065"]
title: "The fleet view"
status: active
owner: user:edwin
created: 2026-08-17
updated: 2026-08-17
tier: 1
area: "Agents and sessions"
covers: ["[[FEAT-0019]]", "[[FEAT-0020]]", "[[FEAT-0032]]"]
related: []
level: acceptance
---

# The fleet view

open `~agents`. Expect: sessions across every workspace, with cost and queue state. — 2026-08-11, **against the running shell over CDP**: header `Agents · 2 active · 0 queued · $1121.48 today · 5h limit 62%`, then a row per workspace — `your-trainer · claude · waiting for you 122h 29m — "Claude is waiting for your input"`, `project-os-cockpit · claude · working <1 min · ctx 46% · $356.92`, and `articles`, `edankert.com`, `Obsidian-Supernote Sync`, `project-os-dev`, `Your Health` idle with their ages. **Cost per session and in aggregate, queue state as a count and as a needs-input row.** *The `project-os-cockpit · working` row was this session, which is the strongest form this check can take: the surface reporting the agent that was reading it.* (user:edwin, 2026-08-11)
