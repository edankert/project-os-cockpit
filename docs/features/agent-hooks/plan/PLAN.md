# Plan — FEAT-0019 Agent hook ingestion

Delivery sequence (tasks to be created via task-breakdown when work starts):

1. **Endpoint + state mapping.** `POST /api/agent-hook` on the sidecar; validation, size caps, event→state mapping into `CockpitState`; SSE fan-out. Testable with curl before any injection exists.
2. **Claude Code injection.** Per-spawn settings injection from `terminal.ts` (generated settings + env; nothing written to `~/.claude`); end-to-end test with a real session.
3. **Codex injection.** `hooks.json` + `notify` program; document the one-time trust prompt.
4. **Statusline forwarder.** Cost/context/rate-limit blob → sidecar; stored on the workspace state for FEAT-0020.
5. **Precedence + decay integration.** Hook-fed vs manual `cockpit signal` arbitration; decay thread applies only to manual/idle sources.

Each step lands with tests (endpoint unit tests in `tests/`, fixture payloads captured from real sessions).
