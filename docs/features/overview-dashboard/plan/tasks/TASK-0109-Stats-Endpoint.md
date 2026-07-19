---
type: "[[task]]"
id: TASK-0109
aliases: ["TASK-0109"]
title: "Server stats endpoint (/api/cockpit/stats)"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
parent: "FEAT-0017"
---

# Stats endpoint

## Definition of Done
- [ ] `stats_payload(index)` in `cockpit.py` returns:
      - `hero` — counts by type (features, tasks, issues, tests, risks)
        + `last_change` summary
      - `status_mix` — `{ type: { status: count } }`
      - `phases` — list of `{ key, title, status, tasks: { done,
        in_progress, backlog } }`
      - `activity` — `{ weekly: [{week_iso, start_date, count}]×13,
        recent: [{id, title, rel, date, features}]×10 }`
- [ ] `/api/cockpit/stats` route on the server returns the payload
      with the standard `X-Cockpit-Schema` header.
- [ ] CHG dates parsed from `CHG-YYYYMMDD-…` ID (no extra IO).
