---
type: "[[task]]"
id: TASK-0629
title: "Show one walk action and its readiness"
status: done
phase: "[[PHASE-043-The-Walk-Page]]"
owner: user:edwin
created: 2026-09-16
updated: 2026-09-24
source: ["Your Trainer FEAT-0122, 2026-09-16"]
parent: "[[FEAT-0151-The-Release-Walk-Has-One-Next-Action]]"
effort: "Large"
depends: []
blocks: ["[[TASK-0630-Record-And-Resume-Walk-Observations]]"]
related: ["[[SUR-0004-The-Release-Walk]]"]
tests: []
---

# Show one walk action and its readiness

## Definition of Done

- [x] The page begins with a compact changed-screen review and then presents one current action with screen, action and exact expected result.
- [x] Before a session, it shows only the setup its retained steps need and any known readiness problem. Required state updates with the authored step.
- [x] Preparation, platform-specific actions and invalid-procedure fallback match the shared generator. Source detail and nearby or full session views remain available on demand.

## Steps

- [x] Sync the upstream generator and expose its new fields in the walk payload.
- [x] Replace the long-scroll walk rendering with focused navigation and a clear main action.
- [x] Test the survey, preparation, platform and fallback views.

## Browser layout finding, 2026-09-16

A real Chrome render of the current Android walk showed the session title twice and nine navigation controls before the action. The page now shows the step count, Review results and Walk options in one compact row. Walk options holds screen, session, step and view navigation; the action card's Continue or Pass and next remains the primary way forward. The focused renderer suite passes 77 cases, and the actual builder and CSS render at 1100 and 700 pixels wide in a standalone Chrome harness. A full Electron walk remains open.

The same render exposed `SUR-0033` as a card heading for Quick Ride cockpit. The shared generator now shows the title from the surface note and keeps the id as the link target. A narrow Chrome render confirms the heading and the light-theme evidence inputs.

Sitting state and equipment now live with the procedure's required setup. The setup opens on a fresh session, closes after the first step, and remains reachable on demand. A focused test and a narrow Chrome render confirm the later-step layout.

The isolated Electron walk found that the session-wide readiness list stayed expanded after the first action and repeated the warning on the current card. It now folds beside the rest of the full setup while the active card keeps its own warning. Walk options offers a step picker with a short action preview and saved mark, so Edwin can jump within the session without creating a verdict. The current Android page resumed at step 12 with the list folded and jumped to step 20. The focused renderer suite passes 80 cases. [[CHG-20260917-Keep-guided-walk-readiness-quiet-after-start-and-add-step-picker]] records the correction.

The synced validator now reports a malformed backticked check tag, and the page payload keeps the owed check in its per-check fallback. A focused test covers a card with both valid and invalid tags; the 36-test payload, bundle and agreement suite passes. Full Electron and human walks remain open.

The current card receives `required_state` from the shared generator. The synced carry-forward rule keeps a declaration through omitted steps on its platform and resets it at the next declaration. Ten preparation fixtures, 36 cockpit payload tests and the focused renderer suite pass; the full Electron and human walk remain open.

A narrow render of the current Android walk showed the screen name and raw `SUR` id again at the start of the visible action. The current card now drops that duplicate when its heading names the same screen; the authored source and exact check quote remain unchanged. The built renderer's 78 focused tests and a later narrow Chrome render confirm it.

## Against the detailed criteria, 2026-09-24

FEAT-0151 now carries the detailed criteria. This task owns the five presentation criteria below; TASK-0630 owns recording and resume. An audit of the current page on 2026-09-24 found these gaps. A criterion is ticked in FEAT-0151 only when a focused test proves it.

- **B1 (survey first):** met in code. A fresh walk opens on one changed screen, Continue needs no ticks, and the survey position is saved. Needs its own test for returning to the survey.
- **B3 (context and progress):** three gaps. Leaving the survey always jumps to step 1 of the first session, so Continue ignores the saved position. The session shows how many steps need attention but not how many are done. Waiting lines, readiness lines and evidence lines use source step numbers where the card heading uses display positions.
- **B4 (flexible focus):** the survey round trip loses the reader's place, because of the B3 gap. Otherwise met.
- **B5 (one action for success):** met, except that keyboard navigation does not exist yet. Arrow keys will move between screens and steps and record nothing.
- **B7 (details on demand):** a step marked fail, partial or question is only a count in the main path. After the walker moves on, the step itself is hidden. The main path will list each such step with its reason and a way back to it.

**Done, 2026-09-24.** All five criteria above are met and ticked in FEAT-0151, each with its own test in `desktop/tests/walk-page.test.mjs`. [[CHG-20260924-The-Walk-Keeps-Problems-In-View-And-Says-Where-You-Resume]] records the change. Verifying the whole walk against the sheet and ledger stays with TASK-0631.
