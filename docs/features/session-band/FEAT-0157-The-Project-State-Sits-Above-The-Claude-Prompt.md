---
type: "[[feature]]"
id: FEAT-0157
aliases: ["FEAT-0157"]
title: "The project's state sits above the Claude Code prompt, and cockpit commands answer there without spending tokens"
status: backlog
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-08
updated: 2026-10-08
source:
  - "Edwin 2026-10-08: 'Plan the implementation in a new phase.'"
  - "[[REFERENCE-FUNCTION-HOOKS-REVIEW]], 'Advisory hooks would stop paying context rent'"
goal: "A person working in a cockpit Claude session sees the focus item and what needs them on one line above the prompt, can open it in the cockpit with one click, and can ask the cockpit a question from the prompt without the model reading the answer."
requirements: []
tasks: []
release: ""
acceptance_exception: ""
acceptance: ""
design: ""
related:
  - "[[FEAT-0156-Claude-Sessions-Report-Through-The-Cockpit-Plugin]]"
  - "[[DES-0015-The-Cockpit-In-Layers]]"
  - "[[PHASE-045-The-Cockpit-In-Layers]]"
  - "[[ISS-0277-Nothing-Detects-A-Stale-Or-Broken-Vendored-Cockpit]]"
---

# The project's state sits above the Claude prompt

**Not started.** Filed at `backlog` in the planned [[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]. It needs the plugin from [[FEAT-0156-Claude-Sessions-Report-Through-The-Cockpit-Plugin]].

## Goal

Above the Claude Code prompt, one band shows the focus item with its status and phase, the validator's error count, the REVIEW-STALE count (finished notes still owing a reply to a review) and the needs-you count, with an "Open in cockpit" button. It costs no tokens, because the model never reads it. A few commands typed at the prompt answer in a pane without starting a turn. When a session starts on a model other than the pinned one, the band says so.

## Findings

- **What draws it.** The mod's `ui.render` hook at the `AbovePrompt` render site, using Box, Text and Button. Drawing appears only in the terminal and in the Desktop app's Code tab; other front ends see nothing, which is acceptable because nothing here is the only place a fact appears.
- **Where the numbers come from.** The sidecar already serves every number: focus from the snapshot payload, needs-you from the obligations breakdown, validator and REVIEW-STALE counts from the validation payload. The band reads them over `$.http.fetch` on a `$.clock.every` timer and on `turn.complete`. It computes nothing itself.
- **This is DES-0015's first layer inside Claude Code.** [[DES-0015-The-Cockpit-In-Layers]] calls it L0, the glance. That design is not accepted ([[PHASE-045-The-Cockpit-In-Layers]]), so this band should use whichever four facts PHASE-045 settles on, and until then the five named above.
- **The model-routing hint (HC-008).** `tools/adapters/claude-code/hooks/model-routing-hint.sh` injects a hint into every prompt that is written for the person, not the model. The band can show the same hint at no token cost. Removing it from the prompt is a change to an upstream-owned hook, so this feature only adds it to the band; the removal is part of the project-os follow-up named in the phase note.
- **Commands.** `$.command.register` with `immediate: true` runs a command with no Claude turn. Built-in names such as `/focus` are reserved, so the names need a prefix (for example `/cockpit-focus`, `/cockpit-validate`, `/cockpit-needs`). A command that returns `{}` and draws in a `Pane` keeps its output away from the model.
- **The pin warning.** CLAUDE.md, "Model routing": a resumed session keeps the model its transcript was saved with, whatever `.claude/settings.json` pins. A `session.start` hook compares the session's model with the pin and shows a line in the band. It does not change the model.
- **The vendored cockpit.** [[ISS-0277-Nothing-Detects-A-Stale-Or-Broken-Vendored-Cockpit]] has no check today. If one is built, the band is a good place to show its result at session start. This feature does not build the check.

### Candidate tasks, minted when this feature starts

1. The band: `ui.render` at `AbovePrompt`, the five facts, the "Open in cockpit" button.
2. The prefixed immediate commands, drawing in a pane.
3. The `session.start` model check against the pin.
4. The routing hint shown in the band.

## Open questions

1. **What does "Open in cockpit" do?** Bring the shell window forward on the focus item through a `cockpit://` link or a sidecar call the shell listens to. Which one exists, or is cheapest, is settled in the plan.
2. **Which commands, under which prefix?** The three above are the suggestion; Edwin picks the prefix.
3. **Does the band wait for PHASE-045's decision on the four facts?** Recommendation: no. Ship the five facts named here and change them when PHASE-045 decides.

## Links

- Phase: [[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]
- Code: `tools/adapters/claude-code/hooks/model-routing-hint.sh` (upstream-owned), `src/project_os_cockpit/obligations.py`
