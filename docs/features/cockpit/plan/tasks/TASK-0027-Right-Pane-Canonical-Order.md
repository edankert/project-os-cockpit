---
type: "[[task]]"
id: TASK-0027
aliases: ["TASK-0027"]
title: "Cockpit: right-pane canonical type order applied to merged linked + inbound-only"
status: done
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-09
updated: 2026-05-09
source: []
implements: ["[[FEAT-0006]]", "[[REQ-0013]]"]
fixes: []
effort: XS
due: ""
depends: []
blocks: []
related: []
tests: ["[[TST-0002]]"]
---

# TASK-0027 — Right-pane canonical type order on merge

## Definition of Done
- [x] `mergeContext` in `cockpit.js` sorts the merged per-type list by the canonical `TYPE_ORDER` from REQ-0013 (`task → feature → issue → requirement → change → phase → release → adr → risk → test → workflow → plan → reference`).
- [x] Types not in the canonical list slot at the end, sorted alphabetically.
- [x] Server-side ordering is unchanged — the bug was JS-side first-appearance ordering.

## Steps
- [x] Added `TYPE_ORDER` and `TYPE_RANK` constants in `cockpit.js` mirroring `cockpit.py`.
- [x] Replaced the `order` accumulator in `mergeContext` with a sort over `Object.keys(byType)` keyed on `TYPE_RANK`.

## Notes
Manually verified for FEAT-0001 in `your-trainer/docs`:
- linked: `requirement, phase`; backlinks-only: `feature, issue, change, release`.
- Pre-fix merged order (first-appearance): `requirement, phase, feature, issue, change, release`.
- Post-fix canonical order: `feature, issue, requirement, change, phase, release`.
