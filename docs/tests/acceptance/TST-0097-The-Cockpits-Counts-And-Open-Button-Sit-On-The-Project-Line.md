---
type: "[[test]]"
id: TST-0097
aliases: ["TST-0097"]
title: "In a cockpit terminal, what needs the person here and elsewhere sits at the end of the project line with an Open in cockpit button, and two commands answer in a pane"
status: active
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[FEAT-0157-The-Project-State-Sits-Above-The-Claude-Prompt]]"]
scope: feature
level: acceptance
entrypoint: "The project line above the prompt, in a new cockpit terminal running claude"
command: ""
last_verified: ""
covers: ["[[FEAT-0157-The-Project-State-Sits-Above-The-Claude-Prompt]]"]
issues: []
tasks: ["[[TASK-0671-The-Shell-Keeps-A-File-Saying-What-Needs-You-In-The-Other-Projects]]", "[[TASK-0672-The-Sidecar-Answers-What-The-Line-Needs-In-One-Request]]", "[[TASK-0673-The-Cockpits-Facts-Join-The-End-Of-The-Project-Line]]", "[[TASK-0674-Open-In-Cockpit-Brings-The-Cockpit-Forward-On-The-Focus-Item]]", "[[TASK-0675-Cockpit-Needs-And-Cockpit-Release-Answer-In-A-Pane-Without-A-Turn]]"]
artifacts: []
adequacy: ""
mutation_score: ""
reviewed_by: ""
review_date: ""
review_verdict: ""
review_round: ""
related: ["[[project-os-dev#TST-0047-A-Claude-Session-Shows-The-Project-Line-And-Names-A-Wrong-Model-And-A-Shell-Edit]]", "[[TST-0096-A-Permission-Prompt-Is-Answered-From-The-Needs-You-Card]]"]
area: ""
after: ["[[TST-0096-A-Permission-Prompt-Is-Answered-From-The-Needs-You-Card]]"]
tags: [test, acceptance, cockpit-plugin, claude-code]
---

# The cockpit's counts and Open button sit on the project line

## Purpose

Confirms what FEAT-0157 promises a person in a cockpit Claude terminal: the cockpit's facts appear at the end of the one line project-os draws, a number that cannot be trusted is left out rather than shown as zero, the button opens the cockpit on the focus item, and the two commands answer without a Claude turn.

## Setup

- The desktop app rebuilt and restarted after FEAT-0157's last task, so the shell writes `needs-elsewhere.json` and the plugin is current.
- project-os-cockpit synced with the project-os template after project-os-dev TASK-0203, so the project-os mod draws its line here.
- At least one other project open in the cockpit with something owed, and one with nothing owed.

## Steps

1. Open a new cockpit terminal on project-os-cockpit and start `claude`. **Expect:** one line above the prompt. It starts with project-os's facts (focus item, status, phase, counts, route) and ends with ` · N need you`, ` · M in other projects` and `[ Open in cockpit ]`. There is no second line or band from the cockpit.
2. Compare with the cockpit window's Needs you badge for this project and with the draft home window. **Expect:** N equals this project's badge total; M equals the sum of the other projects' counts in the home window.
3. Clear what is owed in every other project (or close them), and wait 30 seconds. **Expect:** "in other projects" disappears from the line; it never reads 0.
4. Quit the desktop app, leaving the terminal running (a tmux terminal survives), and wait 2 minutes. **Expect:** the other-projects count disappears. This project's count and the button disappear when the sidecar stops answering.
5. Restart the app. With a focus item set, press `[ Open in cockpit ]` (click it, or ctrl+x tab then its key). **Expect:** the cockpit window comes forward on this project with the focus item's note open.
6. Type `/cockpit-needs`. **Expect:** a pane with this project's owed kinds and each other project's count and source; no Claude turn starts, and nothing about it appears in the transcript. Esc closes it.
7. Type `/cockpit-release`. **Expect:** a pane with the open release's state, matching the cockpit's release page; no Claude turn.
8. Open a plain macOS Terminal in the same repo and start `claude`. **Expect:** the project-os line without the cockpit's segment, and `/cockpit-needs` is not a known command.
9. In a cockpit terminal with `COCKPIT_NO_INSTRUMENT=1` exported before `claude`. **Expect:** no cockpit segment.

## Expected result

Every step's **Expect** holds.
