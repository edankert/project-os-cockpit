---
type: "[[task]]"
id: TASK-0673
aliases: ["TASK-0673"]
title: "In a cockpit terminal, the project line above the Claude prompt ends with what needs the person here, what needs them in the other projects when that is above zero, and an Open in cockpit button"
status: backlog
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[FEAT-0157-The-Project-State-Sits-Above-The-Claude-Prompt]]", "[[project-os-dev#REFERENCE-PROJECT-LINE-CONTRACT]]", "plan/PLAN.md, 'What the line shows, and when it leaves a number out'"]
parent: "[[FEAT-0157-The-Project-State-Sits-Above-The-Claude-Prompt]]"
effort: "M"
due: ""
depends: ["[[TASK-0671-The-Shell-Keeps-A-File-Saying-What-Needs-You-In-The-Other-Projects]]", "[[TASK-0672-The-Sidecar-Answers-What-The-Line-Needs-In-One-Request]]"]
blocks: ["[[TASK-0674-Open-In-Cockpit-Brings-The-Cockpit-Forward-On-The-Focus-Item]]", "[[TASK-0676-The-Lines-Promises-Are-Proved-And-The-Register-Updated]]"]
related: ["[[project-os-dev#TASK-0198-Two-Plugins-Share-The-Line-Above-The-Prompt-Checked-Live]]", "[[project-os-dev#TASK-0202-The-Project-Line-Above-The-Prompt]]"]
tests: []
---

# The cockpit's facts join the end of the project line

**Waits on project-os-dev TASK-0198**, the live check of the drawing contract. Do not start the hook until its findings are in [[project-os-dev#REFERENCE-PROJECT-LINE-CONTRACT]]; if that task stopped for Edwin, his decision comes first.

After this task, a Claude session in a cockpit terminal shows the cockpit's facts at the end of the line project-os draws, for example ` · 3 need you · 5 in other projects  [ Open in cockpit ]`. The plugin draws no line of its own when project-os's is there.

## Definition of Done

- [ ] `register.ts` hooks `ui.render` on `AbovePrompt` under the contract's rules: `next(e)` first; pass a survey through; build a row Box keyed `segment:cockpit`; if the tree beneath has an element keyed `project-os:line`, append the segment as its last child and return the tree; otherwise return the segment alone.
- [ ] The facts are read in the background, never while drawing: `GET /api/cockpit/line` through `sidecarCall`, and `needs-elsewhere.json` through `$.fs.read` from `$COCKPIT_INSTRUMENT_DIR`. Every 10 seconds and after each `turn.complete`. `$.ui.invalidate("ui.render")` only when the segment's text changes.
- [ ] The text follows plan/PLAN.md exactly: this project's count only when above zero; the other projects' sum only when above zero, from known counts under 24 hours old, in a file written within 2 minutes, with a plus when any project is unknown or too old; the button whenever the line route answered.
- [ ] Nothing is drawn when `COCKPIT_NO_INSTRUMENT` is set or no sidecar address is known.
- [ ] `claude plugin test` cases: joined to a fake `project-os:line` when the plugin is outer; returned alone when nothing is beneath; survey passes through; zero here draws no count; a stale file draws no other-projects count; an unknown project adds the plus; a failed line route draws no count and no button.
- [ ] Seen live in a cockpit terminal with the project-os mod loaded (after project-os-dev TASK-0203, or with the template's plugin folder on `CLAUDE_CODE_PLUGIN_DIRS`).
- [ ] Capability register: `shell.agents.claude-plugin` gains a dated line; `shell.agents.project-line` is new.

## Steps

- [ ] The background readers and their cache.
- [ ] The render hook and the join.
- [ ] Tests, live look, register.
