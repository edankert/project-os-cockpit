---
type: "[[task]]"
id: TASK-0674
aliases: ["TASK-0674"]
title: "Pressing Open in cockpit on the project line brings the cockpit window forward on this project's focus item, through a cockpit:// link"
status: backlog
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[FEAT-0157-The-Project-State-Sits-Above-The-Claude-Prompt]]", "FEAT-0157 decision 2"]
parent: "[[FEAT-0157-The-Project-State-Sits-Above-The-Claude-Prompt]]"
effort: "S"
due: ""
depends: ["[[TASK-0672-The-Sidecar-Answers-What-The-Line-Needs-In-One-Request]]", "[[TASK-0673-The-Cockpits-Facts-Join-The-End-Of-The-Project-Line]]"]
blocks: ["[[TASK-0676-The-Lines-Promises-Are-Proved-And-The-Register-Updated]]"]
related: ["[[TASK-0605-A-Cockpit-Link-Opens-The-Page-It-Names]]"]
tests: []
---

# Open in cockpit brings the cockpit forward on the focus item

The line's button is drawn by TASK-0673. After this task a press opens the cockpit window on this project's focus item, or on the project's home when there is no focus item.

## Definition of Done

- [ ] The plugin registers `on("ui.press", { element: "cockpit:open" }, ...)`, so a press reaches it even after the project-os mod has moved the Button into its own line (contract rule 6).
- [ ] It builds `cockpit://<workspace_id>/<open_target>`, or `cockpit://<workspace_id>` when `open_target` is `null`. `workspace_id` comes from `needs-elsewhere.json`; `open_target` from the line route. Both are checked against strict patterns (the workspace ID's form, and `^[A-Z]+-[0-9]+$` for the target) before use; a value that fails draws no button.
- [ ] It runs `$.process.run(["open", url])` on macOS, with an argument list and no shell. A failure shows a toast, "Could not open the cockpit", and nothing else.
- [ ] Checked live: with the cockpit running on another project, a press brings the window forward, switches to this project and opens the focus note. With the focus empty, it opens the project's home.
- [ ] `claude plugin test` cases: the URL for a focus item and for none; a malformed workspace ID or target draws no button and runs nothing.
- [ ] Capability register row `shell.agents.open-in-cockpit`.

## Steps

- [ ] The press handler and the URL.
- [ ] Tests, live check, register.

## Notes

The deep link's project may be the shell's workspace ID (`renderer/deep-link.ts`), so the plugin needs no project-ID mapping. If the live check shows a press from the band has to arm first (the band takes focus with ctrl+x tab or a click), say so in TST-0097's step.
