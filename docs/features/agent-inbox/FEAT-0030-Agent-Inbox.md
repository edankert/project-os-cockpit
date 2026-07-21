---
type: "[[feature]]"
id: FEAT-0030
aliases: ["FEAT-0030"]
title: "Agent inbox — docked attention panel at the bottom of the nav pane, with a sane attention lifecycle"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-19
updated: 2026-07-20
reviewed_by: "model:claude-opus"
review_date: 2026-07-20
review_verdict: approved
goal: "A docked attention panel at the bottom of the left nav pane answers 'what needs me?' at a glance: zero-height when empty, it materialises with needs-input rows (act now) and waiting rows (turn finished — review, with cost) across all workspaces, plus a one-line 'N finished today' link onward; the top-bar bell is deleted. The attention lifecycle stops crying wolf: a normally-finished turn stays amber (idle_prompt no longer escalates to red), and pulses calm to static once seen — pulse means unseen, static means known-and-pending, gone means resolved."
requirements: ["[[REQ-0018-Agent-Attention-Completeness]]"]
tests: []
tasks: ["[[TASK-0147]]", "[[TASK-0156]]", "[[TASK-0157]]"]
related: ["[[FEAT-0020-Agent-Activity-Surfaces]]", "[[ISS-0009-Popovers-Never-Hide]]", "[[FEAT-0032-Agents-Screen]]"]
---

# Agent inbox

## Why

The bell-popover inbox listed only `needs-input`, hid urgency behind a click, and sat diagonally across the window from the rail dots it explains. Worse, the attention lifecycle misfires: a finished turn escalates through the `idle_prompt` notification to a red fast pulse that nothing acknowledges — visiting the workspace changes no state, so it blinks until the next hook event or the 10-minute decay (user reports 2026-07-19). Review artifact §P2-revised/P2b: claude.ai/code/artifact/7011ef1d-f77f-4585-a899-d4ac84a78976.

## Placement (decided 2026-07-19)

Docked at the **bottom of the left nav pane**, below the doc tree behind a hard separator — never interleaved with content. Zero-height when empty. Cross-workspace chrome inside a workspace-scoped pane is deliberate (attention is global; Slack-Activity precedent). The top-bar bell and its popover are removed — one attention surface.

## Scope

- **Panel rows:** active attention only — needs-input (red, message, "respond" jump) and waiting (amber, elapsed + session cost, "review" jump) — sorted urgency-then-recency, per-row dismiss persisted by session-id. Recently-finished collapses to a single "N finished today · agents ›" line (full log lives on ~agents, FEAT-0032; links to the strip/sessions feed until that lands).
- **Severity remap:** `idle_prompt` maps to `waiting`, not `needs-input`; red is reserved for genuinely blocked-mid-work (`permission_prompt`, `elicitation_dialog`). Tracker + external-hook parity.
- **Seen-acknowledgement:** focusing the workspace with the terminal visible (~2s) stops the pulse everywhere (rail ring/dot, panel row emphasis) while keeping the colour — purely visual, no state-data change.

## Out of scope

Cross-workspace session history (FEAT-0032); browser-cockpit parity (open decision on FEAT-0032).
