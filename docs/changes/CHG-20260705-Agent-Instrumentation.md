---
type: "[[change]]"
id: CHG-20260705-Agent-Instrumentation
aliases: ["CHG-20260705-Agent-Instrumentation"]
title: "PHASE-007: hook-fed agent instrumentation — /api/agent-hook, PTY injection, activity strip, needs-input inbox, task dispatch, session insight"
status: merged
owner: user:edwin
created: 2026-07-05
updated: 2026-07-05
impacts:
  - "src/project_os_cockpit/agent_hooks.py (new)"
  - "src/project_os_cockpit/server.py (endpoint + state vocabulary + snapshot/render enrichment)"
  - "desktop/src/ipc/agent-instrument.ts (new)"
  - "desktop/src/ipc/terminal.ts + sidecar.ts (injection wiring)"
  - "desktop/src/ipc/agent-state-poller.ts (needs-input notifications)"
  - "desktop/src/main.ts (dispatch context menu)"
  - "desktop/src/renderer/* (strip, inbox, trail, dispatch, sessions)"
features: ["[[FEAT-0019-Agent-Hook-Ingestion]]", "[[FEAT-0020-Agent-Activity-Surfaces]]", "[[FEAT-0021-Task-Dispatch]]", "[[FEAT-0022-Session-Insight-And-Traceability]]"]
related: ["[[PHASE-007-Agent-Instrumentation]]", "[[RISK-0004-Hook-Injection-Surface]]", "[[TST-0010]]", "[[TST-0011]]"]
---

# PHASE-007 implementation: the terminal understands its agent

## What shipped

**Python sidecar.** New `agent_hooks.py` module + `POST /api/agent-hook`: Claude Code lifecycle hooks (and Codex notify, via `?event=`/`?agent=` query defaults with `thread-id` fallback) are validated, size-capped (2 MB), and folded into the agent-state machine — `UserPromptSubmit` → `busy`, `PermissionRequest`/`Notification(permission_prompt|idle_prompt)` → new state `needs-input`, `Stop` → `waiting`, `SessionEnd` → `idle`; tool events record touched files and refresh busy. New SSE event `cockpit:agent-activity`; `cockpit:agent-state` payloads gain `source: hook`. Manual `cockpit signal` is superseded (acknowledged, not recorded) while a hook session is live and regains authority afterwards. Session index persisted atomically to `.cockpit/sessions.json` (bounded, crash-tolerant seed) and served by `GET /api/cockpit/sessions`. Undocumented-work rule: source files edited with no TASK/ISS/CHG note touched flags the live session. CHG provenance: change notes created during a live session are correlated (watcher) and surfaced via `/api/render.produced_by` — note files are never modified. `/api/cockpit/state` gains `activity` + `session` blocks.

**Desktop injection.** New `agent-instrument.ts` generates per-workspace files under the app's userData (never `~/.claude` / `~/.codex` — RISK-0004): a ZDOTDIR whose `.zshrc` sources the user's real dotfiles then wraps `claude` (adds `--settings <generated hooks+statusline JSON>`) and `codex` (adds `-c notify=[forwarder]`); `hook-forward.sh` (stdin JSON → curl POST, async, 2s cap), `statusline.sh` (debounced cost/context forward + short status echo), `codex-notify.sh` (argv JSON → mapped event). `hook-env` carries the live sidecar URL and is rewritten on every sidecar (re)spawn. Kill switch: `COCKPIT_NO_INSTRUMENT=1`. zsh-only in v1; other shells run uninstrumented.

**Renderer surfaces.** Activity strip above the terminal (state dot, agent, prompt/tool/file, undocumented chip, ctx% + $ meters, expandable files-touched detail). Cross-workspace needs-input inbox (top-bar bell + badge + popover; click jumps to the workspace terminal); OS notifications now fire for `needs-input` transitions too. Live nav trail: notes the agent edits flash an "agent" chip in nav + right pane for 8s. Task dispatch: context-menu "Start with Claude Code / Codex" on TASK/ISS rows and a top-bar ▶ on task/issue notes — types a templated note-first prompt into the workspace PTY (paste-only when the agent is mid-session), remembers the agent per workspace, and sets the focus hint so follow mode picks the item up immediately. Overview gains a live-session banner under the hero (SSE-refreshed: state, prompt, ctx/$ meters, jump-to-terminal), an "Agent sessions" feed column beside Recent activity, and per-session detail pages at `~session/<id>` virtual rels with real history entries (TASK-0127 redesign, replacing the first-cut accordion section). CHG notes render a "produced by session …" provenance line.

## Why

`cockpit signal` (FEAT-0013) is voluntary — the model must remember it. Claude Code/Codex hooks push the same signals structurally; since the desktop shell spawns the PTY, instrumentation is injected per-session with zero agent cooperation. Full rationale + prior-art survey in [[PHASE-007-Agent-Instrumentation]].

## Verification

- Automated: `tests/test_agent_hooks.py` (13 tests, [[TST-0010]] passing); full suite 170 passed, 1 skipped. Desktop `tsc` + build clean.
- Live smoke: synthetic hook POSTs against the running desktop sidecar drove busy → needs-input (persisted with `source: hook`, poller + notification path engaged) → idle; session recorded.
- Pending: [[TST-0011]] manual checklist — real `claude`/`codex` sessions in the embedded terminal (injection end-to-end), visual pass over strip/inbox/trail/dispatch/sessions. TASK-0115/0116 stay `doing` and the features `in-review` until it passes.
