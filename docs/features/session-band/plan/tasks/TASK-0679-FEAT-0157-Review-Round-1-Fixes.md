---
type: "[[task]]"
id: TASK-0679
aliases: ["TASK-0679"]
title: "FEAT-0157 review round 1: the button no longer waits for the other projects' file, the release pane's blocked count is the gate's, one thing owed reads \"1 needs you\", and TST-0097 step 2 matches the code"
status: done
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-21
updated: 2026-10-21
source: ["[[FEAT-0157-The-Project-State-Sits-Above-The-Claude-Prompt]], '## Review', round 1"]
parent: "[[FEAT-0157-The-Project-State-Sits-Above-The-Claude-Prompt]]"
effort: "S"
due: ""
depends: []
blocks: []
related: ["[[TST-0097-The-Cockpits-Counts-And-Open-Button-Sit-On-The-Project-Line]]"]
tests: []
---

# FEAT-0157 review round 1 fixes

Round 1 of FEAT-0157's independent review found these in code and notes the feature changed. Each is fixed here, and round 2 checks them.

## Definition of Done

- [x] The Open in cockpit button takes the workspace ID from the plugin's instrument folder name (`instrument/<ws>`), so it appears as soon as the sidecar answers, before the shell has written `needs-elsewhere.json`. A plugin test shows the button with no such file.
- [x] `/cockpit-release` says "Blocked: N manual checks not settled" with N the length of the gate's own `blocking` list, not the checks owed for the release's contents. A plugin test fails with the old count.
- [x] One thing owed reads "1 needs you"; more read "N need you". A plugin test covers both.
- [x] `home-window.ts`'s comment no longer says the two numbers never disagree: it names the case where the home window shows "not read" and the file a live count.
- [x] TST-0097 step 2 compares only counts under a day old and expects "+" when one is older or missing.
- [x] CLAUDE.md's count of current generated files is today's.
- [x] The plugin suite, the desktop tests and the line route's tests pass.

## Result

- `workspaceOf` takes the button's workspace from `$COCKPIT_INSTRUMENT_DIR`'s last part; `segmentFacts` no longer reads the file's `workspace_id`. New plugin tests: the button with no other-projects file, pressed, runs `open cockpit://ws-7/FEAT-0157`; a folder name that fails the pattern draws no button.
- `releaseRows` counts `gate.blocking`. Live on 2026-10-21 in this repo the gate listed 6 blocking checks while `open_tests` held 3 (TST-0083, TST-0086, TST-0087), so the old pane would have said "Blocked: 3".
- Each old line, put back on its own, failed tests: the file's workspace 3, the `open_tests` count 1, "need" for one 1. Restored: 65 pass.
- Desktop: 229 pass after `npm run build`. Line route and guard tests pass.
