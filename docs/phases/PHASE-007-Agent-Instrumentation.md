---
type: "[[phase]]"
id: PHASE-007
aliases: ["PHASE-007"]
title: "Agent instrumentation (hooks-aware terminal)"
status: done
order: 7
owner: user:edwin
created: 2026-07-05
updated: 2026-07-20
goal: "The embedded terminal understands the agent running inside it: lifecycle hooks feed agent state, activity, cost, and needs-input signals into the cockpit automatically, and the cockpit dispatches project-os tasks back to the agent."
features:
  - "[[FEAT-0019-Agent-Hook-Ingestion]]"
  - "[[FEAT-0020-Agent-Activity-Surfaces]]"
  - "[[FEAT-0021-Task-Dispatch]]"
  - "[[FEAT-0022-Session-Insight-And-Traceability]]"
  - "[[FEAT-0023-Overview-Scopes]]"
  - "[[FEAT-0024-Agent-Verbs]]"
  - "[[FEAT-0025-Dispatch-Runtime]]"
  - "[[FEAT-0026-Verb-Polish]]"
  - "[[FEAT-0027-External-Session-Signal]]"
depends: ["[[PHASE-006-Native-Cockpit-UI]]"]
related: ["[[RISK-0004-Hook-Injection-Surface]]", "[[FEAT-0013-Agent-State-Signal]]"]
---

# Phase 7: Agent instrumentation (hooks-aware terminal)

## Goal

Today the cockpit's agent awareness is voluntary: the LLM must remember to run `cockpit signal` / `cockpit focus` (FEAT-0013, prompted via COCKPIT.md). Meanwhile Claude Code and Codex CLI expose the same signals automatically and structured — Claude Code hooks can POST JSON to a localhost URL on every lifecycle event (`SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `PermissionRequest`, `Notification`, `Stop`, `SessionEnd`), and Codex has an equivalent `hooks.json` plus a `notify` hook (`agent-turn-complete`, `approval-requested`). Because the desktop shell spawns the PTY itself, it can inject this instrumentation invisibly — no agent cooperation required, works even when the model forgets.

On top of that push feed, this phase builds the surfaces that make the cockpit an agent cockpit rather than a docs viewer with a terminal: a live activity strip, a cross-workspace needs-input inbox, dispatching TASK notes to the agent from the task board, and doc-traceability features (undocumented-work badge, session↔CHG linking) that only a tool that knows the project-os contract can offer.

## Scope

### In scope
- **FEAT-0019 — Agent hook ingestion.** New sidecar endpoint (`POST /api/agent-hook`), hook injection at PTY spawn for Claude Code (http hooks via settings injection) and Codex (`hooks.json` + `notify`), statusline forwarder for cost/context/rate-limit data, mapping hook events into the existing `CockpitState` agent-state machine and SSE fan-out. `cockpit signal` stays as the fallback for external terminals.
- **FEAT-0020 — Agent activity surfaces.** Activity strip above the terminal (current prompt, current tool + file, context-fill and cost meters), cross-workspace needs-input inbox with jump-to-terminal, live attribution trail in the nav (badge the note the agent just touched).
- **FEAT-0021 — Task dispatch.** "Start with agent" on TASK/ISS notes: type a templated prompt into the workspace PTY (agent choice: Claude Code / Codex), wired to follow mode so the dispatched work is visible end-to-end.
- **FEAT-0022 — Session insight and traceability.** Per-workspace session history browser (transcript JSONL on disk), undocumented-work badge (code edited but no TASK/ISS/CHG note touched this session), stamping session id/cost into CHG notes.

### Out of scope
- Inline diff review, PR auto-fix/auto-merge, embedded preview browsers, cloud execution — Claude Desktop, Codex app, and Conductor own that space; the cockpit stays a docs-first surface.
- Parallel worktree sessions / multi-PTY per workspace. Real architectural lift; deferred until single-agent instrumentation proves out.
- Editing notes from the cockpit (standing constraint — the cockpit is a viewer).
- Driving agents headlessly (`claude -p` / `codex exec`) from the cockpit. Dispatch types into the interactive PTY; owning a headless loop is a possible future phase.
- Support beyond Claude Code + Codex in v1 (opencode/Gemini/aider adapters can follow the same endpoint contract later).

## Exit Criteria
- [ ] Launching `claude` inside the embedded terminal flips the workspace rail dot busy/waiting/needs-input with zero manual `cockpit signal` calls, and a permission prompt raises an OS notification within a second.
- [ ] The activity strip shows the agent's current prompt, the file it is editing, and live cost/context meters during a real session.
- [ ] The needs-input inbox aggregates blocked agents across at least two workspaces and jumps to the right terminal on click.
- [ ] A TASK note can be dispatched to the agent from the nav context menu and the resulting work is observable via follow mode.
- [ ] A session that edits `src/**` without touching any TASK/ISS/CHG note shows the undocumented-work badge.
- [ ] `cockpit signal` / external-terminal behaviour unchanged (mode 1 and non-instrumented agents keep working).

## Notes
- **Sequencing.** FEAT-0019 first — it is the data pipe everything else consumes (same pattern as FEAT-0013 before FEAT-0010 in PHASE-006). Then FEAT-0020 (visible payoff), then FEAT-0021 and FEAT-0022 in either order.
- **Trust boundary.** `/api/agent-hook` accepts unauthenticated localhost POSTs; payloads must be treated as untrusted input (validated, size-capped, never rendered as HTML). See [[RISK-0004-Hook-Injection-Surface]].
- **Config etiquette.** Hook injection must not mutate the user's own `~/.claude` / `~/.codex` configuration; injection is per-spawn (env/flags/generated files under the app's own state dir). Codex hooks may require a one-time trust prompt in the TUI — surface that honestly in the UI.
- **Prior art** (researched 2026-07-05): Crystal/Nimbalyst session status indicators, Antigravity's Inbox for blocked agents, vibe-kanban's board-as-queue, Warp's per-tab agent status, Sculptor's session history. Differentiator here: the project-os knowledge graph — dispatch from durable TASK notes and guardrails that know the documentation contract.

## Close-out (2026-07-20)

All in-scope features and tasks are complete (FEAT-0018..0037 done, tasks 0114..0173 resolved). The phase's exit criteria above are left unchecked deliberately: they correspond to TST-0011, the manual live-agent e2e checklist (launch a real claude/codex, trigger a permission prompt, observe OS notifications) that the user chose to waive in favour of the automated verification performed across the 2026-07-20 sweep (instrumentation-pipeline smoke test against the sidecar, CDP UI checks, 409 identity guard, 218 passing unit tests, per-feature independent reviews). The criteria remain the record of what a human pass would confirm.
