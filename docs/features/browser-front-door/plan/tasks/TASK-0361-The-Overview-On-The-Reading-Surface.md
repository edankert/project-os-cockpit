---
type: "[[task]]"
id: TASK-0361
aliases: ["TASK-0361"]
title: "The project overview renders in the browser cockpit from the same stats payload"
status: backlog
phase: "[[PHASE-029-One-Tool-Two-Front-Doors]]"
owner: user:edwin
created: 2026-08-09
updated: 2026-08-09
source: ["[[ADR-0010-What-The-Browser-Cockpit-Is-For]]"]
parent: "[[FEAT-0083-The-Browser-Cockpit-Answers-Questions]]"
effort: M
due: ""
depends: ["[[ADR-0010-What-The-Browser-Cockpit-Is-For]]"]
blocks: []
related: []
tests: []
---

# The overview on the reading surface

## Definition of Done
- [ ] Mode 1 has an Overview view rendering `/api/cockpit/stats`: focus band, stat tiles, phase accordion with the Completed band, history
- [ ] Phase scope rows work — selecting a phase scopes the overview, as in the shell
- [ ] No control on the page issues a write

## Steps
- [ ] Add the view to `cockpit.js` and its rules to `cockpit.css`, reusing existing tokens
- [ ] Port the tile / accordion / squares rendering; the squares' six marks are DES-0004's and their precedence order is load-bearing (ISS-0071)
- [ ] Check the empty cases a fresh corpus hits: no phases, no focus, no commits

## Notes
The payload has existed since PHASE-008 and mode 1 has simply never consumed it. Watch the shared-vocabulary trap while porting: the mark precedence (`archived` tested before `_is_done`) and the status buckets come from `statuses.py` — restating either here is the ISS-0023 failure a third time, and `tests/test_status_vocabulary.py` already parses this file.
