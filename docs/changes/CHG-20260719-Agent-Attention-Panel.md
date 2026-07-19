---
type: "[[change]]"
id: CHG-20260719-Agent-Attention-Panel
aliases: ["CHG-20260719-Agent-Attention-Panel"]
title: "Docked agent attention panel + honest severity + seen-acknowledgement (bell removed)"
status: merged
owner: user:edwin
created: 2026-07-19
updated: 2026-07-19
source: []
commit: ""
pr: ""
impacts: ["nav pane (new attention panel)", "top-bar bell removed", "agent_hooks Notification mapping", "external hook script", "rail dot / attention pulse acknowledgement"]
issues: []
features: ["[[FEAT-0030-Agent-Inbox]]"]
reviewed_by: "model:claude-opus"
review_date: 2026-07-19
review_verdict: approved
related: ["[[REQ-0018-Agent-Attention-Completeness]]", "[[TASK-0156]]", "[[TASK-0147]]", "[[TASK-0157]]"]
---

# Agent attention panel (FEAT-0030)

## Summary

The agent attention surface moved from a top-bar bell popover to a panel docked at the bottom of the left nav pane, and the attention lifecycle was made honest.

**TASK-0156 — severity remap (Python).** `idle_prompt` notifications no longer escalate a finished turn to the red `needs-input` tier; the tracker maps them to amber `waiting`, reserving `needs-input` for genuine mid-work blocks (`permission_prompt`, `elicitation_dialog`). `agent_hooks.py` splits `_NEEDS_INPUT_NOTIFICATIONS` / `_WAITING_NOTIFICATIONS`; the external-hook embedded script (`app-settings.ts`) gains a matching subtype gate on its file-fallback path (the forwarded path already routes through the tracker). This is the fix for the "session finished but the item keeps blinking red" report.

**TASK-0147 — docked panel (renderer).** New `#ws-attention` below `#ws-nav-content` (hard separator, `flex:none`, zero-height when empty): needs-input rows (red, "respond") above waiting rows (amber, elapsed + session cost when known, "review"), cross-workspace, urgency-then-recency; a "N finished today · sessions ›" one-liner from an observed-transition tally (interim until the ~agents fleet log, FEAT-0032). Per-row dismiss persisted in localStorage keyed by `(workspace, state-ts)` — a new transition mints a fresh alert. The top-bar bell, badge, and popover (and their CSS) are deleted; the Overview Now-card "needs" block now reuses the same cross-workspace entries.

**TASK-0157 — seen-acknowledgement (renderer).** Pulse now means "unseen": when the active workspace's window is focused with the terminal visible for 2s, its current alert is acknowledged — the rail dot pulse and needs-input ring go static while the colour stays, and the panel row loses its pulse. Keyed on `(workspace, state-ts)`, so a genuinely new alert re-pulses. Purely visual; no state data, decay, or notification behaviour changes.

## Verification

- Python: `tests/test_agent_hooks.py` (idle_prompt→waiting, permission→needs-input, unknown subtype no-op) and `tests/test_external_hook.py` (file-fallback subtype gate) updated; full suite 209 passed, 1 skipped.
- Renderer: driven end-to-end over the Chrome DevTools Protocol against the running app — panel populates cross-workspace with correct ordering; dismissal removes a row and is ts-keyed (same ts stays dismissed, new ts reappears); acknowledgement turns an active alert static (dot + ring `animation-name: none`) while keeping needs-input colour, and a new-ts alert re-pulses; CSS `.acked` wiring confirmed. `tsc --noEmit` clean.

Independent review (opus) approved with two low-severity nits, both folded in: `openWorkspace` now nulls `lastAgentSnap` on switch so a newly-active waiting row can't briefly show the previous workspace's cost; and `ackedAlerts` is pruned to live `(workspace, state-ts)` keys each time an ack lands, so it can't grow unbounded over a long session. Re-verified over CDP after the fixes (ack fires with focus+terminal confirmed; new-ts alerts re-pulse).

Files: `src/project_os_cockpit/agent_hooks.py`, `desktop/src/ipc/app-settings.ts`, `desktop/src/renderer/{index.html,renderer.ts,renderer.css}`, `tests/test_agent_hooks.py`, `tests/test_external_hook.py`.
