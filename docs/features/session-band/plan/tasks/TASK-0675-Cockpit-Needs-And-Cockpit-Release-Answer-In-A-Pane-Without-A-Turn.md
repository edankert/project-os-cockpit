---
type: "[[task]]"
id: TASK-0675
aliases: ["TASK-0675"]
title: "/cockpit-needs and /cockpit-release, typed at the Claude prompt in a cockpit terminal, answer from the sidecar in a pane without starting a Claude turn"
status: backlog
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[FEAT-0157-The-Project-State-Sits-Above-The-Claude-Prompt]]", "FEAT-0157 decision 1", "project-os-dev REFERENCE-COCKPIT-SIMPLIFICATION-SORT, 2026-10-13: the two questions the cockpit CLI cannot answer"]
parent: "[[FEAT-0157-The-Project-State-Sits-Above-The-Claude-Prompt]]"
effort: "M"
due: ""
depends: ["[[TASK-0671-The-Shell-Keeps-A-File-Saying-What-Needs-You-In-The-Other-Projects]]", "[[TASK-0672-The-Sidecar-Answers-What-The-Line-Needs-In-One-Request]]"]
blocks: ["[[TASK-0676-The-Lines-Promises-Are-Proved-And-The-Register-Updated]]"]
related: []
tests: []
---

# /cockpit-needs and /cockpit-release answer in a pane without a turn

Today, to learn what waits across projects or where a release stands, the person leaves the terminal for the cockpit window or asks Claude, which spends a turn and reads the answer into the context. After this task two commands answer at once, in a pane the model never reads. They exist only in cockpit terminals, because they live in the cockpit's own plugin.

## Definition of Done

- [ ] `$.command.register` with `immediate: true` for `cockpit-needs` and `cockpit-release`, each with a one-line description. Each returns `{}` and opens a `Pane` with `$.ui.open`, so no Claude turn starts and nothing enters the model's context.
- [ ] `/cockpit-needs` draws this project's kinds from `GET /api/cockpit/line` ("2 features to review"), then each other project from `needs-elsewhere.json` with its count and where the count came from: "live", "counted <time> ago", or "not read". Projects with nothing owed are listed last, dimmed.
- [ ] `/cockpit-release` draws what `GET /api/cockpit/release` returns for this project: the open release, its status, and what is still owed before it ships, in the words the cockpit's release page uses.
- [ ] When the sidecar does not answer, the pane says "The cockpit is not answering for this project" and shows nothing else. A missing `needs-elsewhere.json` says "The cockpit shell has not written the other projects' counts".
- [ ] The pane closes with Esc and leaves no trace in the transcript.
- [ ] `claude plugin test` cases: each command starts no turn; each pane's text for a fixture answer; the not-answering text.
- [ ] Checked live in a cockpit terminal.
- [ ] Capability register row `shell.agents.prompt-commands`.

## Steps

- [ ] Command registration and the pane.
- [ ] The two drawings.
- [ ] Tests, live look, register.

## Notes

Read `release_payload`'s shape (`src/project_os_cockpit/publication.py`) before drawing; if a field the release page shows is computed in the renderer rather than the payload, either move that computation into the payload or leave it out and say so here.
