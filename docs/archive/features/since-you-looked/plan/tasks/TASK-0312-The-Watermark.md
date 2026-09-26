---
type: "[[task]]"
id: TASK-0312
aliases: ["TASK-0312"]
title: "The watermark, and the Caught-up that moves it"
status: done
phase: "[[PHASE-026-The-Returning-Human]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[FEAT-0071-Since-You-Looked]]"]
parent: "[[FEAT-0071-Since-You-Looked]]"
effort: S
depends: []
blocks: []
related: []
tests: []
---

# The watermark, and the Caught-up that moves it

## Definition of Done

- [x] `.cockpit/last-seen.json` per workspace; GET/POST endpoints; only the explicit `Caught up` action moves it — opening the app never does.
- [x] Missing watermark reads as epoch: the first digest shows everything, honestly.

## Done 2026-08-10

`src/project_os_cockpit/watermark.py`, `GET /api/cockpit/watermark` and `POST /api/cockpit/caught-up`. Crash-tolerant temp-file-and-replace, matching `ReviewStore`.

**Both criteria are about what it must *not* do**, and so are the tests:

- **Only `catch_up` moves it.** `test_only_catch_up_moves_it` exercises every read path first and asserts the marker is still unset. Presence is not attention; a watermark that moves itself turns the digest into a slot machine.
- **Unset reads as the epoch**, never as *now*. Defaulting to now would report a quiet project because the install had no memory rather than because nothing happened — the same lie in a different shape.

**A corrupt store degrades to unset**, which is the safe direction: unset means *show everything*, so a truncated write loses the marker rather than hiding a backlog.

### Two judgments not in the DoD

**`catch_up` takes the digest's timestamp, not the click's.** Otherwise anything landing while the human reads is silently marked seen — which is the same defect as a self-moving watermark, arriving through the back door.

**The endpoint is loopback-guarded** although it writes runtime state rather than `docs/`. It records *this human's* attention, and a LAN peer marking someone else caught up would silently empty their digest. Guarded and asserted.
