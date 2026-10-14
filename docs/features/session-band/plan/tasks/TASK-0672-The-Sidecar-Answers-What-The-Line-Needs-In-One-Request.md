---
type: "[[task]]"
id: TASK-0672
aliases: ["TASK-0672"]
title: "GET /api/cockpit/line answers, in one loopback request, this project's needs-you total with its kinds and the note the Open in cockpit button should open"
status: backlog
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[FEAT-0157-The-Project-State-Sits-Above-The-Claude-Prompt]]", "plan/PLAN.md, 'GET /api/cockpit/line'"]
parent: "[[FEAT-0157-The-Project-State-Sits-Above-The-Claude-Prompt]]"
effort: "S"
due: ""
depends: []
blocks: ["[[TASK-0673-The-Cockpits-Facts-Join-The-End-Of-The-Project-Line]]", "[[TASK-0674-Open-In-Cockpit-Brings-The-Cockpit-Forward-On-The-Focus-Item]]", "[[TASK-0675-Cockpit-Needs-And-Cockpit-Release-Answer-In-A-Pane-Without-A-Turn]]"]
related: ["[[REQ-0027-Every-Write-Guarded]]"]
tests: []
---

# The sidecar answers what the line needs in one request

The plugin could piece the line together from the obligations route and the snapshot, but then the plugin would own the rule for which focus item the button opens, and two clients would compute the count. After this task one read-only route gives the plugin both, computed by the code the badges already use.

## Definition of Done

- [ ] `GET /api/cockpit/line` in `server.py`, loopback only, returning the shape plan/PLAN.md gives: `schema_version`, `needs_you.total`, `needs_you.kinds` (kind, count, verb, noun), and `open_target`.
- [ ] `needs_you.total` comes from `obligations.badges_payload` and equals its `total` for the same index. `kinds` sums the breakdown across views, with the verb and noun from the same payload, singular or plural by count.
- [ ] `open_target` is `focus.task`, else `focus.issue`, else `focus.feature`, else `focus.phase`, else `null`, read the way the sidecar already reads the snapshot.
- [ ] A failure while computing returns 500 with an error, never a zero count.
- [ ] Python tests that fail when: the total differs from `/api/cockpit/obligations`'s; a non-loopback request is answered; an empty focus gives anything but `null`; a computing error returns 200.
- [ ] Capability register row `api.read.line`.

## Steps

- [ ] The route and its function.
- [ ] Tests and register row.
