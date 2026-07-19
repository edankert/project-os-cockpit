---
type: "[[task]]"
id: TASK-0155
aliases: ["TASK-0155"]
title: "Surface rots batch — transcript link, queue tooltip, undocumented wording, feed staleness"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-19
updated: 2026-07-19
source: []
parent: "FEAT-0033"
effort: ""
due: ""
depends: []
blocks: []
related: []
tests: []
---

# TASK-0155 — surface rots

Four small inconsistencies from the review: (1) session-page transcript path becomes an action (reveal in Finder); (2) queue-chip static tooltip says "click to clear" while click manages — fix the HTML copy; (3) "undocumented" is worded four ways across strip/feed/session-page/Now — pick one label; (4) the sessions feed only refetches while on ~overview — force a refetch on re-entry so live pills/durations don't go stale. Verification: manual sweep of each surface.
