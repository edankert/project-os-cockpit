---
type: "[[plan]]"
title: "Plan — the write service widens"
status: active
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
parent: "[[FEAT-0059-The-Write-Service-Widens]]"
---

# Plan

1. **[[TASK-0278]]** — the human-owned transition table as data, and `/api/notes/transition`. The table is the deliverable; the endpoint is plumbing through existing guards.
2. **[[TASK-0279]]** — the tick path: locate criterion by text under the criteria heading, rewrite one line, both forms (`[x]` with evidence + witness, `[~]` with reason). mtime-guarded so a stale match cannot apply.
3. **[[TASK-0280]]** — `/api/notes/create` for issues, and the hardening suite for all three verbs: every refusal tested by attempting the forbidden thing, per the module's existing test style.
