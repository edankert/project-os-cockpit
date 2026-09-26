---
type: "[[change]]"
id: CHG-20260706-Dispatch-Runtime
aliases: ["CHG-20260706-Dispatch-Runtime"]
title: "Dispatch runtime + verb polish — main-process queue, ledger, CLI, status-aware verbs, palette"
status: merged
owner: user:edwin
created: 2026-07-06
updated: 2026-07-06
impacts:
  - "desktop/src/ipc/dispatch-queue.ts (new — queue + delivery state machine in main)"
  - "desktop/src/ipc/terminal.ts + sidecar.ts (writeToPty / sidecarUrlFor exports)"
  - "desktop/src/ipc/agent-state-poller.ts (delivery trigger for all workspaces)"
  - "src/project_os_cockpit/agent_hooks.py (dispatch ledger + requests store)"
  - "src/project_os_cockpit/agent_actions.py (when-lists)"
  - "src/project_os_cockpit/server.py (/api/cockpit/dispatch, /dispatch-requests, render dispatch_history)"
  - "src/project_os_cockpit/cli.py (cockpit dispatch)"
  - "desktop/src/renderer/* (queue popover, provenance, palette verbs, status-aware menus)"
features: ["[[FEAT-0025-Dispatch-Runtime]]", "[[FEAT-0026-Verb-Polish]]"]
related: ["[[PHASE-007-Agent-Instrumentation]]", "[[TST-0014]]", "[[CHG-20260706-Agent-Verbs]]"]
---

# Dispatch becomes a first-class, tracked unit of work

## What shipped

**Main-process dispatch runtime (FEAT-0025).** The queue moved out of the renderer into `dispatch-queue.ts` in the Electron main process — beside the PTYs and the cross-workspace poller it depends on. Queues are persisted under userData (restored on launch, capped at 20/workspace); `dispatch:execute` decides enqueue-vs-deliver from the workspace's last known agent state; delivery fires on state transitions for **any** workspace (poller for background ones, SSE poke for the active one), typing into that workspace's own PTY — REPL mode after `Stop` with a live session, single-quote-escaped shell command otherwise (fixes the `$(…)`/backtick injection hole). REPL delivery warns when the live session's agent differs from the chosen one; missing-PTY delivery re-queues with a warning. The strip's queue chip now opens a popover with per-item remove and clear-all.

**Dispatch ledger.** `POST /api/cockpit/dispatch` records `{id, verb, agent}` on the session tracker; pending dispatches stamp the next session that starts (live sessions get them directly); sessions expose `dispatches`, session feed rows show "← verb ID", the detail page gains a "Dispatched from" section, and `/api/render` carries `dispatch_history` — rendered as a provenance line on the note ("dispatched refine · claude · … → session … (live)") and backing a re-dispatch confirmation when the note's dispatch is still live.

**`cockpit dispatch` CLI.** `cockpit dispatch TASK-0115 --verb refine --agent claude` posts a queue-request; the desktop picks it up via the `cockpit:dispatch-request` SSE event (open workspace) or the once-only `GET /api/cockpit/dispatch-requests` drain on sidecar attach, resolves the verb template, and runs the normal execute path. Agents can now queue work for the cockpit from any terminal.

**Verb polish (FEAT-0026).** Registry entries carry `when: [statuses]` and every verb surface filters by the row's status (nav rows via new `data-type`/`data-status` attributes, the ▶ button via the open note's frontmatter status, scoped feature rows via their payload) — no more "Implement" on done tasks. ⌘P understands verb prefixes: "refine TASK-0115" filters to matching types, badges rows with "▶ Refine", and Enter dispatches instead of navigating. Type resolution prefers row data over ID-prefix guessing, so custom `actions.yaml` types surface. Dead code from the first cut removed.

## Verification

- [[TST-0014]] passing (7 tests); full suite 186 passed, 1 skipped; `tsc` + build clean.
- Live smoke: dispatch record → once-only request handoff → `dispatch_history` on the note's render payload, against this repo's docs.
- Interactive pass (queue popover, background-workspace delivery, palette dispatch) rides on [[TST-0011]].
