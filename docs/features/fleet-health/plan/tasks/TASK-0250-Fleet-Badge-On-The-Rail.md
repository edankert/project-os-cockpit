---
type: "[[task]]"
id: TASK-0250
aliases: ["TASK-0250"]
title: "The validator badge on the workspace rail and tabs, without colliding with the agent-state dot"
status: done
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
- [~] Each workspace rail entry and tab carries a tri-state validator signal: clean / drifting-with-count / unknown
- [x] It does **not** collide with the existing agent-state dot — the collision is resolved deliberately, and the resolution is written down
- [x] The tooltip carries the error count and `checked_at`, and says whether the state is live or cold
- [x] `unknown` is visually distinct from `clean` — a repo nobody has checked must not read as a repo that passed
- [x] Distinguishable without colour, and under `prefers-reduced-motion` if any motion is used

## Steps
- [~] Resolve the channel question (below), preferably against a rendered comparison rather than in prose
- [x] Render from the IPC state [[TASK-0248]] provides; no fetching in the renderer
- [x] Test: a source-level guard that the two signals use different elements or attributes, plus a live check across two workspaces in differing states

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

## Done 2026-07-30 — the channel question, resolved on semantics

Three options were on the table (a second mark elsewhere / fold into one dot with precedence / tab-only). **Option 1**, but the reason it works is not "there is space in the other corner" — it is that the two signals differ in *three* independent ways at once, so neither depends on the reader having learned a colour:

| | agent state | validator state |
|---|---|---|
| position | bottom-right | **top-left** |
| shape | circle | **rounded pill** |
| content | blank fill | **a numeral** |

The numeral is what makes this work rather than merely fit. It carries the error count, which a dot cannot, and a digit is the least colour-dependent mark available. That is [[DES-0004]]'s method rather than its output: there, colour was already spent on type so attention took shape; here position *and* colour are spent on agent state, so this takes shape and information.

**No design-bench pass was run, and that is a judgement call.** This note asked for one, on the grounds that three options at rail width is cheaper to look at than to argue. It resolved on semantics instead — the marks differ in kind, not in taste, so there was no comparison to make. If it reads badly in the app, that is a finding against this decision.

### The encoding

- `failing` → count badge, top-left. `99+` above 99.
- `ok` → hairline ring on the square (`inset box-shadow`, `--status-done`). Quiet: the common case must not compete with the exceptional one.
- `unavailable` → hairline ring in `--text-faint`. "Asked, got no answer."
- `unknown` → **nothing at all**. Not a grey mark; no mark. Never asked.
- `stale` → same mark, hollowed.

**`unknown` painting nothing is the requirement, not a default.** [[ISS-0065]] was a surface whose unbuilt cards looked exactly like cards with nothing to say. A fleet dashboard whose default state reads as healthy teaches people to read absence as health. Guarded by `unknown paints nothing, and only failing gets a numeral`, which asserts the early return happens **before** the badge is constructed — mutation-verified by removing it.

### Two repaint paths that must not clobber each other

Agent state arrives far more often than validator state, and `applyAgentStateToSquare` rewrites `li.title` wholesale. The tooltip is now composed from `li.dataset.baseTitle` — agent state owns the base, health appends to it — and every agent repaint re-applies health. Without that the badge survived (classes untouched) while its tooltip line silently vanished.

`the validator badge and the agent dot never share an element or a class` asserts the separation structurally, including that no CSS rule mentions both. Mutation-verified by moving the badge to the dot's corner.

**Tabs: not done.** This repo's mode-3 shell has a workspace *rail*, not a tab strip — the DoD's "and tabs" describes a surface that does not exist here. Said plainly rather than ticked.

## Live pass 2026-07-30 — verified against the real fleet, and it found a defect elsewhere

Ten discovered workspaces, one deliberately drifted (a `METRICS` error induced in this repo's own `SNAPSHOT.yaml`, trivially reversible).

**Both signals coexist on the same square.** `project-os-cockpit` carried `class="ws-square active state-busy health-failing"` with badge `1` — agent state and validator state at once, which is the collision this task exists to avoid.

```
project-os-cockpit   state-busy  health-failing  badge "1"
  title: "…\nagent: busy\ndocs: 1 validator error (open, checked just now)"
articles             state-waiting health-ok     badge null
  title: "…\nagent: waiting — Claude is waiting for your input\ndocs: clean (not open, checked just now)"
… 9 more, all health-ok, no badge
```

**The badge cleared over SSE without a restart**: `health-failing` + `1` → `health-ok`, no badge, tooltip `docs: clean (open, checked just now)`.

**The tooltip composition holds.** Every square carries both lines — agent state from `baseTitle`, docs health appended — across repeated agent-state repaints, which is what the `dataset.baseTitle` split was for.

### Found while doing it, and filed as [[ISS-0072]]

The first attempt to clear the drift did **not** work: restoring `SNAPSHOT.yaml` left the sidecar reporting `failing` with an unchanged `checked_at` through three separate edits. A docs-tree write cleared it immediately. `ValidationRunner`'s project-root observer — the one whose docstring exists to catch `SNAPSHOT.yaml` edits — does not fire.

That is [[FEAT-0018]]'s machinery, not this task's, and this task's path is unaffected: once the sidecar produced a new report, it propagated to the rail correctly. Recorded rather than worked around.

### Fixed while doing it

The initial cold pass ran at `app.whenReady`, before workspace discovery had populated, so it validated nothing and every repo sat `unknown` until the 10-minute timer. Delayed 4 s, for the same reason `main.ts`'s janitor is delayed. Measured before and after.
