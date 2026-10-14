---
type: "[[feature]]"
id: FEAT-0157
aliases: ["FEAT-0157"]
title: "The cockpit's facts join the project line above the Claude Code prompt, and cockpit commands answer there without spending tokens"
status: backlog
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-08
updated: 2026-10-14
source:
  - "Edwin 2026-10-08: 'Plan the implementation in a new phase.'"
  - "[[REFERENCE-FUNCTION-HOOKS-REVIEW]], 'Advisory hooks would stop paying context rent'"
  - "Edwin 2026-10-14, in project-os-dev, on which mod uses belong in project-os and which in the cockpit: 'yes, file them and update FEAT-0157'"
goal: "A person working in a cockpit Claude session sees, on the project line above the prompt, what the cockpit knows and the repo cannot: what needs them in this project and in the others, with a button that opens it in the cockpit. Commands typed at the prompt ask the cockpit a question without the model reading the answer."
requirements: []
tasks: []
release: ""
acceptance_exception: ""
acceptance: ""
design: ""
related:
  - "[[FEAT-0156-Claude-Sessions-Report-Through-The-Cockpit-Plugin]]"
  - "[[project-os-dev#FEAT-0041-Project-Os-Mod]]"
  - "[[project-os-dev#ISS-0106-Project-Os-As-A-Plugin]]"
  - "[[FEAT-0160-A-Draft-Window-Shows-What-Needs-You]]"
  - "[[DES-0015-The-Cockpit-In-Layers]]"
  - "[[PHASE-045-The-Cockpit-In-Layers]]"
  - "[[ISS-0277-Nothing-Detects-A-Stale-Or-Broken-Vendored-Cockpit]]"
---

# The cockpit's facts join the project line above the Claude prompt

**Not started.** Filed at `backlog` in the planned [[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]. It needs the plugin from [[FEAT-0156-Claude-Sessions-Report-Through-The-Cockpit-Plugin]], and the project line from [[project-os-dev#FEAT-0041-Project-Os-Mod]].

## Goal

One line above the Claude Code prompt shows where the project stands. Its project half belongs to project-os, because it can be read from the repo and should appear in every session, in every repo, inside the cockpit or not. That half is the focus item with its status and phase, the validator's error count, the routing hint, and the wrong-model warning. This feature adds the cockpit's half to the same line: how many things need the person in this project, how many in the other projects, and an "Open in cockpit" button. It also adds commands that ask the cockpit a question at the prompt and answer in a pane, without starting a turn. Nothing on the line costs tokens, because the model never reads it.

## Scope

**In this feature (the cockpit's half):**

- The needs-you count for this project, and the count for every other open project, from the sidecar's obligations breakdown.
- An "Open in cockpit" button that brings the cockpit forward on this project's focus item.
- Prefixed commands that answer from the sidecar, drawn in a pane: what is owed across projects (`/cockpit-needs`), and where a release stands (`/cockpit-release`). These are the two questions the `cockpit` CLI cannot answer today, per the 2026-10-13 sort note in project-os-dev.

**Moved to project-os on 2026-10-14 ([[project-os-dev#FEAT-0041-Project-Os-Mod]]):**

- The focus item, its status and phase, and the validator's error and REVIEW-STALE counts. All of these are read from the repo.
- The `session.start` check that the session's model matches the pin. A resumed session on the wrong model happens outside cockpit terminals too.
- The routing hint (HC-008) on the line instead of in the model's context. The hook is owned by project-os.
- Commands that only run a repo's own scripts (`/pos-q <ID>`, `/pos-validate`, `/pos-where`).

## Findings

- **One line, drawn once.** The project-os mod draws the line. When the session runs in a cockpit terminal, the mod also asks the sidecar for the cockpit's facts and adds them. The shell already sets `COCKPIT_HOOK_URL` in the terminal, which names the sidecar. Two mods each drawing a line above the prompt would give the person two bands to read, so this feature does not draw its own band.
- **What this feature has to deliver, then.** It does not draw. It provides a sidecar answer shaped for the line (the counts and the button's target), the commands, and the button's action. Whether the commands live in the cockpit's plugin or are served to the project-os mod is open question 1.
- **Where the numbers come from.** The sidecar already serves them: needs-you from the obligations breakdown, release state from `/release`. The draft home window ([[FEAT-0160-A-Draft-Window-Shows-What-Needs-You]]) reads the same answers for every project, so the line and the window show the same numbers.
- **Commands.** `$.command.register` with `immediate: true` runs a command with no Claude turn. Built-in names such as `/focus` are reserved, so the names carry a prefix. A command that returns `{}` and draws in a `Pane` keeps its output away from the model. A command's answer is computed by code, not by the AI, so its counts can be trusted.
- **This is DES-0015's first layer inside Claude Code.** [[DES-0015-The-Cockpit-In-Layers]] calls it L0, the glance. That design is not accepted ([[PHASE-045-The-Cockpit-In-Layers]]), so the line uses whichever facts PHASE-045 settles on.
- **The vendored cockpit.** [[ISS-0277-Nothing-Detects-A-Stale-Or-Broken-Vendored-Cockpit]] has no check today. If one is built, the line is a good place to show its result at session start. This feature does not build the check.
- **Drawing appears only in the terminal and the Desktop app's Code tab.** Other front ends see nothing. That is acceptable, because the cockpit's windows show every fact on the line.

### Candidate tasks, minted when this feature starts

1. A sidecar answer shaped for the line: this project's needs-you count, the other projects' counts, and the button's target.
2. The "Open in cockpit" action.
3. `/cockpit-needs` and `/cockpit-release`, drawn in a pane.

## Open questions

1. **Where do the cockpit commands live?** In the cockpit's own plugin from FEAT-0156, which loads only in cockpit terminals, or in the project-os mod, which calls the sidecar when `COCKPIT_HOOK_URL` is set? Recommendation: the cockpit's plugin, so project-os never names a cockpit command.
2. **What does "Open in cockpit" do?** It could bring the shell window forward through a `cockpit://` link, or through a sidecar call the shell listens to. The plan settles which one exists or is cheapest.
3. **Do the other projects' counts belong on the line at all?** They help when the person works in one project while another waits on them. They also put a second project's business in this one's terminal. Edwin decides.

## Links

- Phase: [[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]
- The project half: [[project-os-dev#FEAT-0041-Project-Os-Mod]]
- Code: `src/project_os_cockpit/obligations.py`, `desktop/src/ipc/home-window.ts` (the draft window's reads)
