---
type: "[[change]]"
id: CHG-20261014-The-Cockpits-Facts-Join-The-Project-Line
title: "In a cockpit Claude terminal, the line above the prompt ends with what needs you here and in the other projects and an Open in cockpit button, and two commands answer from the cockpit in a pane"
status: merged
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[TASK-0671-The-Shell-Keeps-A-File-Saying-What-Needs-You-In-The-Other-Projects]]", "[[TASK-0672-The-Sidecar-Answers-What-The-Line-Needs-In-One-Request]]", "[[TASK-0673-The-Cockpits-Facts-Join-The-End-Of-The-Project-Line]]", "[[TASK-0674-Open-In-Cockpit-Brings-The-Cockpit-Forward-On-The-Focus-Item]]", "[[TASK-0675-Cockpit-Needs-And-Cockpit-Release-Answer-In-A-Pane-Without-A-Turn]]", "[[TASK-0676-The-Lines-Promises-Are-Proved-And-The-Register-Updated]]"]
commit: ""
pr: ""
impacts: ["desktop/plugin/claude-code/hooks/register.ts", "desktop/plugin/claude-code/.claude-plugin/plugin.json", "desktop/src/ipc/needs-count.ts", "desktop/src/ipc/needs-elsewhere.ts", "desktop/src/ipc/needs-elsewhere-file.ts", "desktop/src/ipc/home-window.ts", "desktop/src/ipc/agent-instrument.ts", "desktop/src/ipc/sidecar.ts", "desktop/src/main.ts", "src/project_os_cockpit/cockpit.py", "src/project_os_cockpit/server.py", ".github/workflows/observed-coverage.yml"]
platforms: [macos]
issues: []
features: ["[[FEAT-0157-The-Project-State-Sits-Above-The-Claude-Prompt]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[TST-0097-The-Cockpits-Counts-And-Open-Button-Sit-On-The-Project-Line]]", "[[RISK-0004-Hook-Injection-Surface]]", "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]", "[[project-os-dev#FEAT-0041-Project-Os-Mod]]"]
---

# The cockpit's facts join the project line

## Summary

In a Claude terminal the cockpit opened, the line above the prompt now ends with the cockpit's own facts: how many things need you in this project, how many in the other projects, and an Open in cockpit button. The line itself is drawn by project-os's plugin (project-os-dev FEAT-0041), which every synced repo now loads; the cockpit's plugin adds its part to the end. Two commands, `/cockpit-needs` and `/cockpit-release`, answer from the cockpit in a pane beside the transcript without starting a Claude turn.

## What a person notices

- **The line above the prompt**, for example `TASK-0675 doing · PHASE-046 · 0 validator errors · 11 review-stale · route: implement here · 6 need you · 340+ in other projects [ Open in cockpit ]`. Everything up to the route is project-os's; the rest is the cockpit's. There is one line, not two.
- **A number is left out rather than shown wrong.** This project's count shows only when above zero. The other projects' count shows only when above zero, from counts less than a day old, in a file the shell refreshed within the last 2 minutes. It reads `5+` when some project could not be read. A sidecar that does not answer removes this project's count and the button.
- **Open in cockpit** brings the cockpit window forward on this project, at the focus item's note, or on the project when nothing is in focus.
- **`/cockpit-needs`** lists what is owed here by kind ("2 designs to accept"), then each other project with its count and where it came from: `live`, `counted 3h ago`, or `not read`. Projects owing nothing come last, dimmed.
- **`/cockpit-release`** says where the next release stands: prepared or not, how many items, how many manual checks block it, and what is still owed.
- **A narrow terminal** cuts the cockpit's part first; project-os's facts stay whole as long as they fit.
- **Nothing changes in a terminal the cockpit did not open**: the project-os line appears there without the cockpit's part, and the two commands do not exist.

## Impact

- **The sidecar** gains `GET /api/cockpit/line`, loopback-only and read-only: this project's needs-you total (the badges' own number), its kinds, and the focus item the button opens. A failure is a 500, never a zero.
- **The shell** writes `needs-elsewhere.json` into every workspace's instrument folder every 30 seconds, and when a sidecar starts or exits. The draft home window now counts through the same function (`ipc/needs-count.ts`); what it draws is unchanged.
- **The cockpit plugin** draws for the first time (its segment and two panes), registers two slash commands, and runs one command (`open cockpit://…`, with an argument list and checked parts). It is now tested on Claude Code 2.1.300, and the `observed-coverage` workflow pins that version.
- **Capability register:** `api.read.line`, `shell.fleet.needs-elsewhere`, `shell.agents.project-line`, `shell.agents.open-in-cockpit` and `shell.agents.prompt-commands` are new; `shell.agents.claude-plugin` gains a dated line.
- **RISK-0004** names the new file and the one command, and records that Claude Code, not the cockpit, now writes the project-os marketplace's registration under `~/.claude`.

## What was checked

- Python: `tests/test_line_route.py`, four tests. Node: `desktop/tests/needs-elsewhere.test.mjs`, four tests. Plugin: `tests/line.test.ts`, 18 cases, beside the 44 existing ones, which pass unchanged. Every promise in the plan's "What the implementation must not do" has a test that was shown to fail with its guard removed.
- Live, in Claude Code 2.1.300, in this repository: the joined line with both plugins loaded, `/cockpit-needs`'s pane with no turn started, and the segment giving way first with a pane docked. The sidecar was one running this code on a temporary worktree, so the running app was not disturbed.

## What was not checked

- **The button was not pressed live**, because that would have switched the running cockpit window. It is TST-0097 step 5.
- **The shell's own writer has not run in the app.** The app needs a restart on this build. The live look used a file written by the shell's built counting and writing code, called directly.
- **The real counts** need the walk: TST-0097 steps 2 to 4 compare them with the badges and the home window.

## Documentation Coverage (All Types Considered)

- features: updated (FEAT-0157)
- requirements: not-applicable
- tasks: updated (TASK-0671 to TASK-0676)
- issues: not-applicable
- tests: new (`test_line_route.py`, `needs-elsewhere.test.mjs`, `line.test.ts`); updated (TST-0097's steps)
- workflows: updated (`observed-coverage.yml` pins Claude Code 2.1.300)
- decisions: not-applicable
- risks: updated (RISK-0004)
- changes: new
- snapshot: updated
