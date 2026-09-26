---
type: "[[task]]"
id: TASK-0147
aliases: ["TASK-0147"]
title: "Docked attention panel — bottom of the nav pane, needs-input + waiting + finished one-liner; bell deleted"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-19
updated: 2026-07-19
source: ["[[REQ-0018-Agent-Attention-Completeness]]"]
parent: "FEAT-0030"
effort: ""
due: ""
depends: ["[[TASK-0156]]"]
blocks: []
related: ["[[ISS-0009-Popovers-Never-Hide]]", "[[TASK-0157]]"]
tests: []
---

# TASK-0147 — docked attention panel

Replace the bell-popover inbox with a panel docked at the bottom of `#ws-nav`, below the tree behind a hard separator (mockup: review artifact §P2-revised): zero-height when empty; needs-input rows (red, message, "respond" jump) and waiting rows (amber, elapsed + session cost, "review" jump) across all workspaces, urgency-then-recency; per-row dismiss persisted by session-id (localStorage); recently-finished collapses to "N finished today · agents ›" (interim link: sessions feed). Delete `#top-bar-inbox`, `#inbox-badge`, `#inbox-popover` and their handlers/CSS. Verification: seed three workspaces across the row kinds — panel materialises, ordering/dismissal/jumps correct, empty state takes no space, no bell remains.
