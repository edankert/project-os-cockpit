# Plan — FEAT-0030 Agent inbox

Order: 0156 → 0147 → 0157 (remap is a tiny data fix that immediately stops the worst false alarm; the panel builds on calmer semantics; acknowledgement polishes every pulsing surface last).

1. **TASK-0156.** Severity remap: `idle_prompt` out of the needs-input set in the tracker; external-hook script parity (coordinates with TASK-0153's subtype gate).
2. **TASK-0147.** Docked attention panel at the bottom of the nav pane (zero-height empty, needs-input + waiting rows, finished one-liner, per-row dismiss); delete the top-bar bell + popover.
3. **TASK-0157.** Seen-acknowledgement: renderer/poller `ack` map keyed on (workspace, state-ts); pulse → static on focus+terminal-visible ~2s; applies to rail dot/ring and panel rows.
