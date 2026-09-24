# Plan — FEAT-0019 Agent hook ingestion

Delivery sequence (tasks to be created via task-breakdown when work starts):

1. **Endpoint + state mapping.** `POST /api/agent-hook` on the sidecar; validation, size caps, event→state mapping into `CockpitState`; SSE fan-out. Testable with curl before any injection exists.
2. **Claude Code injection.** Per-spawn settings injection from `terminal.ts` (generated settings + env; nothing written to `~/.claude`); end-to-end test with a real session.
3. **Codex injection.** `hooks.json` + `notify` program; document the one-time trust prompt.
4. **Statusline forwarder.** Cost/context/rate-limit blob → sidecar; stored on the workspace state for FEAT-0020.
5. **Precedence + decay integration.** Hook-fed vs manual `cockpit signal` arbitration; decay thread applies only to manual/idle sources.

Each step lands with tests (endpoint unit tests in `tests/`, fixture payloads captured from real sessions).

## Codex parity follow-up — 2026-09-23

1. [[TASK-0633]] attempts the complete live Electron lifecycle walk first.
2. [[TASK-0634]] closes observed subagent and interruption gaps, then [[TASK-0635]] extends the external-session feature.
3. [[TASK-0636]] investigates usage read-only; [[TASK-0637]] reconciles guidance and records enforcement limits.

The initial walk establishes the baseline; fixes and documentation may proceed while a live row remains pending. Return to every affected row after implementation. PHASE-040 stays deferred. No historical waiver or fixture run becomes a fresh live pass.

## Handoff, 2026-09-23

Codex lifecycle and external opt-in code is implemented and tested. TASK-0636 and TASK-0637 are complete. The quoted-status parser correction is fixed upstream and synced here. TASK-0633 retains the incomplete live walk; TASK-0634 and TASK-0635 retain their TST-0011 completion gate. Finish that evidence and fresh independent review before closing either feature.
