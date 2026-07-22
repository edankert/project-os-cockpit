# Plan — FEAT-0038 Console progress rail

Order: 0188 → 0189 → 0190 (the rail is the headline user ask; the panel enrichment builds on the same extended transition store; the rename/chevron is a cosmetic finisher that should land with or after the panel so the "progress" name matches richer content).

1. **TASK-0188.** Progress rail: second thin row under the collapsed strip, live `.ov-phase-sq` blocks per session work item, click/hover, overflow cap, active-item pulse.
2. **TASK-0189.** Progress panel: rich recency-ordered rows (block + id + title + from→to + relative time), active item pinned; extend `workTransitions` to `{from, to, ts, title}` (shared foundation with 0188's fills).
3. **TASK-0190.** Rename `work` → `progress`; replace the "files" text expand button with a rotating chevron.

All three are renderer-only (`desktop/src/renderer/`): the `cockpit:status-change` SSE payload and session `work_notes` already carry everything needed. Clear the rail/panel state on workspace switch alongside `stripLastPrompt`/`workTransitions` (ISS-0015 pattern).
