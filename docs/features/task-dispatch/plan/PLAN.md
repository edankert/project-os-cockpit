# Plan — FEAT-0021 Task dispatch

Independent of FEAT-0020; benefits from FEAT-0019 for round-trip visibility.

1. **Prompt templates + resolution.** Template set (dispatch/fix/resume) with id/path/title substitution; per-agent variants (claude, codex).
2. **Context-menu + doc-header wiring.** "Start with agent" on task/issue rows and the centre-pane header; busy-session detection → paste-only mode.
3. **Agent picker + persistence.** Per-workspace last-agent memory (localStorage), small picker UI.
4. **Follow-mode integration.** Dispatch sets the agent-focus hint so the existing follow mode and FEAT-0020 strip surface the work immediately.
