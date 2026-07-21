---
type: "[[feature]]"
id: FEAT-0025
aliases: ["FEAT-0025"]
title: "Dispatch runtime — main-process queue, dispatch ledger, CLI"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-06
updated: 2026-07-20
reviewed_by: "model:claude-opus"
review_date: 2026-07-20
review_verdict: approved
verification_waiver: "TST-0011 is a manual live-agent e2e checklist (real claude/codex launch, permission prompt, OS notification). User accepted the automated verification in lieu of the manual pass on 2026-07-20: instrumentation-pipeline smoke test (generated scripts → sidecar tracker), CDP UI checks, 409 sidecar-identity guard, 217 passing unit tests, and an independent review verdict of CLOSE for all five."
goal: "Dispatch becomes a tracked, workspace-independent unit of work: the queue lives in the Electron main process (persisted, delivering into any workspace's PTY on that workspace's own state transitions), every dispatch is recorded in a sidecar ledger and stamped onto the session it starts, and `cockpit dispatch` lets agents and scripts enqueue work from any terminal."
requirements: []
tests: ["[[TST-0014]]", "[[TST-0011]]"]
tasks: ["[[TASK-0134]]", "[[TASK-0135]]", "[[TASK-0136]]"]
related: ["[[FEAT-0024-Agent-Verbs]]", "[[FEAT-0022-Session-Insight-And-Traceability]]"]
---

# Dispatch runtime

## Why

The FEAT-0024 review found the queue architecturally misplaced: it lived in the renderer, pinned to the active workspace — queued work for a background workspace never delivered, an app restart lost the queue silently, and dispatch itself was fire-and-forget (no record connecting a dispatch to the session it started or the change it produced). PTYs and the cross-workspace agent-state poller live in the main process; the queue and its delivery state machine belong beside them, and the session index is the natural home for dispatch provenance.

## Scope

1. **Main-process queue** (TASK-0134). `dispatch-queue.ts`: per-workspace queues persisted under userData; `dispatch:execute` IPC decides enqueue-vs-deliver from the workspace's last known agent state; delivery on state transitions from the poller (all workspaces) and an SSE-fed fast path for the active one; REPL-vs-shell delivery mode resolved against the workspace's own sidecar; queue-changed events fan to all windows; renderer queue popover (list, remove-one, clear). Single-quote shell escaping. Delivery targets the queue's own workspace PTY regardless of which workspace is on screen.
2. **Dispatch ledger** (TASK-0135). `POST /api/cockpit/dispatch` records `{id, verb, agent}` on the tracker; pending dispatches are stamped onto the next session that starts (same correlation pattern as CHG notes); sessions expose their originating dispatches; `/api/render` gains `dispatch_history` for TASK/ISS/FEAT/REQ/PHASE/RISK notes; the renderer shows provenance on notes and session rows, and warns when re-dispatching a note whose dispatch is already live.
3. **CLI** (TASK-0136). `cockpit dispatch <ID> [--verb v] [--agent a]` posts a queue-request to the sidecar; requests persist and are picked up by the desktop shell (SSE for the open workspace, fetch-on-attach for the rest), which resolves the verb template and runs the normal execute path.

## Out of scope

- Auto-spawning a PTY for a workspace that has none — queued work waits for a terminal to exist.
- Cross-repo dispatch routing (one sidecar = one workspace remains the boundary).

## Acceptance

- Queue work in workspace A, switch to workspace B: when A's agent hits Stop/SessionEnd, the queued prompt is typed into A's PTY anyway; an app restart preserves undelivered queues.
- The queue popover lists pending dispatches with per-item remove.
- A dispatched note's page shows "dispatched <verb> → session … ($…)"; the session detail names its originating dispatch; re-dispatching a live-dispatched note warns first.
- `cockpit dispatch TASK-0115 --verb refine` from any terminal under the workspace lands in the queue/PTY like a menu dispatch (ledger-recorded, TST-0014).
