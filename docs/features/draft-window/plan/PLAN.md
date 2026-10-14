---
type: "[[plan]]"
title: "Delivery plan: the draft window"
status: active
owner: user:edwin
created: 2026-10-13
updated: 2026-10-13
source: ["[[FEAT-0160-A-Draft-Window-Shows-What-Needs-You]]"]
implements: ["[[FEAT-0160-A-Draft-Window-Shows-What-Needs-You]]"]
related: ["[[PHASE-045-The-Cockpit-In-Layers]]", "[[FEAT-0152-Home-First]]"]
---

<!-- Plans deliberately carry no `id:` / `aliases:`; see docs/__templates__/plan.md. -->
# Delivery plan: the draft window

The draft window is built in three steps, each a task. All code lands under `desktop/src/`. Nothing under `src/project_os_cockpit/` changes unless open question 3 of the feature note applies.

## Delivery sequence

1. **The window and its data** ([[TASK-0646-The-Draft-Window-Opens-From-The-Menu-And-Gathers-Every-Projects-Data]]). The main process (`desktop/src/main.ts`) gains a menu item that opens a second window of a new kind, with its own page and its own preload bridge. A new module under `desktop/src/ipc/` gathers one payload for that window: per project, the owed rows, the active phase's state and the AI session's state. It reads the sidecars the shell already runs and the session state the shell already polls (`ipc/agent-state-poller.ts`, `ipc/agents-fleet.ts`). The same step adds the channel by which the draft window asks the main process to open a `cockpit://` link in the present window.
2. **The page** ([[TASK-0647-The-Draft-Windows-Page-Shows-Three-Areas-And-Opens-The-Present-Window]]). A new page under `desktop/src/renderer/` draws the three areas from that payload. The parts that turn the payload into rows are pure functions in a file of their own, loaded as a plain script the way `deep-link.ts` is, so they can be tested without a window. The page does not import or change `renderer.ts`.
3. **Harness, tests and the register** ([[TASK-0648-Harness-Unit-Tests-And-A-Register-Row-For-The-Draft-Window]]). A harness page under `desktop/harness/` shows the draft page in a browser. Unit tests under `desktop/tests/` cover the pure functions. The capability register gains its row in the same commit as the change note, and the acceptance check moves from `draft` to `active`.

Steps 2 and 3 can overlap: writing the tests beside the pure functions is the cheaper order. Step 1 goes first because the page needs a real payload to be judged against.

## Dependencies

- **Hard:** none outside this feature. The routes the draft reads exist: `/api/cockpit/obligations` (owed counts per view), `/api/cockpit/landing?view=` (the owed rows of one view), `/api/cockpit/stats?scope=PHASE-####` (one phase's numbers) and `/api/cockpit/state` (the session). The `cockpit://` link is handled in `main.ts` (`handleDeepLink`) and parsed in `renderer/deep-link.ts`.
- **Soft:** `ipc/fleet-health.ts` already tells live projects (a sidecar is running) from cold ones and reads the cold ones another way. Reusing it keeps the draft from starting a sidecar per project.

## What the implementation must not do

- Change a page of the present window, or `renderer.ts`.
- Add or change a write route on the sidecar, or call one from the draft window.
- Put a console, a second session per project or a per-session branch into this feature. Those are later steps (feature note, "Later steps").
- Let the draft window become the window that receives `cockpit://` links. `handleDeepLink` sends to `mainWindow`, and that must stay the present window.

## Open questions

- The three in the feature note, each with its default: cold projects, which copy of the present window a link opens, and whether a new read-only route is needed.
- **What "what is next" and "what still stands between the phase and finished" are computed from.** Default: "next" is the phase's items at `backlog` or `planned` in the order the Features view lists them, and "what still stands" is the phase's unticked exit criteria plus the notes that would stop it closing (`phase_close_blockers` in `cockpit.py`). If the existing stats payload does not carry these, this is where open question 3 applies.
- **How a session's state maps to working, stuck or waiting.** Default: reuse the words the rail and the Needs you panel already derive from the poller's states, so the two windows never disagree about one session.
