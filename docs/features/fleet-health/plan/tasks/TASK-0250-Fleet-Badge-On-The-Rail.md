---
type: "[[task]]"
id: TASK-0250
aliases: ["TASK-0250"]
title: "The validator badge on the workspace rail and tabs, without colliding with the agent-state dot"
status: backlog
phase: "[[PHASE-013-Fleet-Surfaces]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["[[FEAT-0028-Fleet-Health-Surface]]"]
parent: "[[FEAT-0028-Fleet-Health-Surface]]"
effort: M
depends: ["[[TASK-0248-Live-Workspace-Validation-Aggregate]]"]
blocks: []
related: ["[[DES-0004-Attention-In-The-Squares]]", "[[TASK-0082-Workspace-Rail-Dots]]"]
tests: []
---

# TASK-0250 — The badge on the rail

## Definition of Done
- [ ] Each workspace rail entry and tab carries a tri-state validator signal: clean / drifting-with-count / unknown
- [ ] It does **not** collide with the existing agent-state dot — the collision is resolved deliberately, and the resolution is written down
- [ ] The tooltip carries the error count and `checked_at`, and says whether the state is live or cold
- [ ] `unknown` is visually distinct from `clean` — a repo nobody has checked must not read as a repo that passed
- [ ] Distinguishable without colour, and under `prefers-reduced-motion` if any motion is used

## Steps
- [ ] Resolve the channel question (below), preferably against a rendered comparison rather than in prose
- [ ] Render from the IPC state [[TASK-0248]] provides; no fetching in the renderer
- [ ] Test: a source-level guard that the two signals use different elements or attributes, plus a live check across two workspaces in differing states

## The channel question

The rail entry already carries `.ws-dot`, which is **agent state** ([[TASK-0082]]) — idle, working, needs-input. Adding a validator dot to the same element puts two independent signals on one channel, in a space smaller than a phase square.

This is [[DES-0004]]'s budget problem again, and that design's lesson applies: colour was already spent on type there, so attention took shape instead. Here, the dot's *position and colour* are already spent on agent state.

Options, none free:
1. **A second mark in a different position** — e.g. a corner pip on the tab, leaving the rail dot alone. Cheapest; risks two small marks competing at rail width.
2. **Fold into one dot with precedence** — agent state wins while a session is live, validator state shows otherwise. Loses simultaneity exactly when both matter.
3. **Badge on the tab only, not the rail** — the rail stays agent-only. Narrowest, and the roll-up ([[TASK-0251]]) carries the fleet-wide answer instead.

**Worth rendering before choosing.** [[DES-0004]] settled a harder version of this question in one pass because four treatments were shown side by side at true density; three options at rail width is a smaller exercise and the design bench already exists. If the answer is not obvious in prose, it is a DES note, not a debate.

## Notes

`unknown` mattering as much as `drifting` is the non-obvious requirement. A fleet dashboard whose default state is indistinguishable from *pass* teaches people to read absence as health — the failure [[ISS-0065]] was about, where cards that stopped being built looked exactly like cards with nothing to say.
