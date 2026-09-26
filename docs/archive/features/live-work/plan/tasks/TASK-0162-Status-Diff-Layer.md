---
type: "[[task]]"
id: TASK-0162
aliases: ["TASK-0162"]
title: "Status-diff layer — note saves become transition events (cockpit:status-change)"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-19
updated: 2026-07-19
source: []
parent: "FEAT-0036"
effort: ""
due: ""
depends: []
blocks: ["[[TASK-0163]]", "[[TASK-0164]]"]
related: []
tests: ["[[TST-0018]]"]
---

# TASK-0162 — status-diff layer

Foundation for every live-work view. The sidecar's watcher already fires per note save; add a frontmatter-status differ keyed by note id: on change, emit `cockpit:status-change {id, rel, type, title, from, to, ts}` over SSE (additive event — schema unchanged) and append to a capped recent-transitions log exposed at `GET /api/cockpit/transitions`. Index rebuilds must not fire spurious transitions (diff against the previous known status, not absence). Verification: pytest — save with status change → one event + log entry; save without status change → nothing; cold index → nothing.
