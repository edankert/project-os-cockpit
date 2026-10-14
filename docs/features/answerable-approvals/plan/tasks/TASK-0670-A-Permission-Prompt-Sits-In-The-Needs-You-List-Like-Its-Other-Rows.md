---
type: "[[task]]"
id: TASK-0670
aliases: ["TASK-0670"]
title: "A permission prompt sits in the Needs you list like its other rows, with Approve and Deny as two words at the end of its session line"
status: done
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["Edwin 2026-10-14, walking TST-0096: 'It all works but I don't like the way the buttons are displayed and the way it creates a section with a border around it.'", "Edwin's choice the same evening: 'Text actions on the meta line'"]
parent: "[[FEAT-0159-A-Permission-Prompt-Is-Answered-From-The-Cockpit]]"
effort: "S"
due: ""
depends: ["[[TASK-0666-The-Needs-You-Card-Answers-A-Permission-Prompt]]"]
blocks: []
related: ["[[TST-0096-A-Permission-Prompt-Is-Answered-From-The-Needs-You-Card]]"]
tests: []
---

# A permission prompt sits in the Needs you list like its other rows

TASK-0666 drew each permission prompt as a box of its own: a red border, a shaded background, and two full-width outlined buttons underneath. Edwin saw it on the first run of TST-0096 and did not like the buttons or the bordered box. After this task the prompt is a plain row, like the other Needs you rows. The command sits under the title, marked by a thin line on its left, and "Approve · Deny" are two coloured words at the right end of the session line.

What the card says does not change, and neither does what a click does. The command is still shown whole and never cut.

## Definition of Done

- [x] The row has no border and no background of its own. It gets the same hover shade as the other Needs you rows. (`.ws-approval-row` in `renderer.css`.)
- [x] The command, the session line and the terminal note line up with the project name, not with the dot. (`.ws-approval-row > :not(.ws-approval-head)` is indented 16px.)
- [x] The command block has a thin rule on its left instead of a filled background. It still wraps and scrolls, and is never cut. (The existing "a long command is not cut" test still passes.)
- [x] Approve and Deny are text buttons with no border, separated by `·`, at the right end of the session line. Approve is green and Deny is red. Both are disabled while the answer is in flight. (`buildApprovalRow` puts them in `.ws-approval-meta`; `answerApproval` still disables both.)
- [x] A prompt handed to the terminal shows its "Answer in the terminal" sentence where the words were, and no buttons. (The note line is unchanged and indented like the others.)
- [x] `desktop/tests/approval-card.test.mjs` still passes, and a test fails if the row gets a border again. (7 pass. With `border: 1px solid red` put back on the row, 1 fails.)
- [x] Seen in the live application after a rebuild. (Edwin, 21:57, after a window reload: "I have seen it, all good for now!")

## Handoff, 2026-10-14 21:55

- **Done:** the renderer and stylesheet changes and the test. `npm run build` in `desktop/` ran at about 21:54. Only the renderer changed, so a window reload (Cmd+R) is enough to see it. The app does not need a restart.
- **Next:** Edwin reloads the window and says "reloaded". The agent runs `touch /tmp/tst-0096-3b.txt`, and Edwin looks at the new card and presses Deny. That also retries TST-0096 step 3. In the first try, `touch /tmp/tst-0096-3.txt` was recorded as granted (approval `6488c88d8a71`, 20:46:35 UTC), and Edwin said "It all works", so it was probably a press of Approve. If he likes the card, tick the last box and set this task `done`.
- **Edwin's decision, in his words:** "I don't like the way the buttons are displayed and the way it creates a section with a border around it." He chose "Text actions on the meta line" over small right-aligned buttons, and over ✓ and ✕ icons beside the title.
- **21:58, after the reload:** `touch /tmp/tst-0096-3b.txt` ran with no card and no approval record. The session had most likely left manual mode, since the plugin offers asks only in manual or acceptEdits mode. Waiting for Edwin to switch back with Shift+Tab and say "ready". The retry is `touch /tmp/tst-0096-3c.txt`, which Edwin Denies. The record before the reload shows ten grants from cards, and one handover to the terminal at 20:50:16, which is step 4 passing again.
- **21:55, back in manual mode** (the session had been in plan mode). `touch /tmp/tst-0096-3c.txt` drew a card at 20:54:45 UTC. Nobody clicked within 5 s, so it was handed to the terminal at 20:54:50 and approved there. The next call was approved from the new card at 20:54:59, so the new Approve button works. The Deny is still untried. Asked Edwin whether Deny did not respond or the 5 s ran out, and whether the new layout is what he wanted. If he says "again", run `touch /tmp/tst-0096-3d.txt` for him to Deny.
- **TST-0096 so far:** this walk runs in this repository's own cockpit terminal (session `3c410600`) in manual mode, not in deck. Steps 1, 2 and 4 pass (Edwin: "It all works"). The step 7 deny hook is installed in `project-os-deck/.claude/settings.local.json`. That file is gitignored and did not exist before, so delete it after step 7.
