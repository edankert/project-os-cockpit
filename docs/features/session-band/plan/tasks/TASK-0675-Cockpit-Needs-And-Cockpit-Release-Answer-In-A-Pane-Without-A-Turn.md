---
type: "[[task]]"
id: TASK-0675
aliases: ["TASK-0675"]
title: "/cockpit-needs and /cockpit-release, typed at the Claude prompt in a cockpit terminal, answer from the sidecar in a pane without starting a Claude turn"
status: done
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

- [x] `$.command.register` with `immediate: true` for `cockpit-needs` and `cockpit-release`, each with a one-line description. Each returns `{}` and opens a `Pane` with `$.ui.open`, so no Claude turn starts and nothing enters the model's context.
- [x] `/cockpit-needs` draws this project's kinds from `GET /api/cockpit/line` ("2 features to review"), then each other project from `needs-elsewhere.json` with its count and where the count came from: "live", "counted <time> ago", or "not read". Projects with nothing owed are listed last, dimmed.
- [x] `/cockpit-release` draws what `GET /api/cockpit/release` returns for this project: the open release, its status, and what is still owed before it ships, in the words the cockpit's release page uses.
- [x] When the sidecar does not answer, the pane says "The cockpit is not answering for this project" and shows nothing else. A missing `needs-elsewhere.json` says "The cockpit shell has not written the other projects' counts".
- [x] The pane closes with Esc and leaves no trace in the transcript.
- [x] `claude plugin test` cases: each command starts no turn; each pane's text for a fixture answer; the not-answering text.
- [x] Checked live in a cockpit terminal.
- [x] Capability register row `shell.agents.prompt-commands`.

## Steps

- [x] Command registration and the pane.
- [x] The two drawings.
- [x] Tests, live look, register.

## Notes

Read `release_payload`'s shape (`src/project_os_cockpit/publication.py`) before drawing; if a field the release page shows is computed in the renderer rather than the payload, either move that computation into the payload or leave it out and say so here.

## Result (2026-10-14)

Live check, Claude Code 2.1.300, in this repository: a session with the project-os plugin from the repo, the cockpit plugin on `CLAUDE_CODE_PLUGIN_DIRS`, and an instrument folder of its own. Its `hook-env` named a sidecar running this code on a temporary worktree, so the running app's sidecar and `.cockpit/url` were untouched. Its `needs-elsewhere.json` was written by the shell's built `needs-count.js` and `needs-elsewhere-file.js` from the other projects' live sidecars. `/cockpit-needs` opened a docked pane reading `This project` / `2 designs to accept` / `2 requirements to approve` / `1 ADR to decide` / `1 commit to push` / `Other projects` / one row per project with its count and `live` or `not read`. The debug log shows the command listed, the pane placed, and no turn started. Esc closed it.

`/cockpit-release` shows the release's name and whether it is prepared, its item count since the last release, whether manual checks block it and how many, and up to eight still-owed items. That is a subset of the release page, read from `GET /api/cockpit/release` as it is. The page's words for the other parts (settle, coverage, confidence) are computed in the renderer, so they are left out rather than copied.

Tests, in `tests/line.test.ts`: each pane's rows for a fixture answer; the not-answering and no-file sentences; each command opens its pane, returns no text and submits no prompt. A command that returns text turns one red.
