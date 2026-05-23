---
type: "[[feature]]"
id: FEAT-0002
aliases: ["FEAT-0002"]
title: "Live reload via Server-Sent Events"
status: done
phase: "[[PHASE-001-MVP]]"
owner: user:edwin
created: 2026-05-07
updated: 2026-05-23
source: []
goal: "When any .md under the served docs/ tree changes, the corresponding browser pages soft-reload within a fraction of a second."
release: ""
related: ["[[FEAT-0001]]", "[[FEAT-0003]]"]
requirements: ["[[REQ-0004]]"]
tasks: ["[[TASK-0005]]", "[[TASK-0006]]"]
---

# Live reload via SSE

## Goal
The render server watches the served `docs/` directory and pushes file-change notifications to connected browsers over a Server-Sent Events channel. Each rendered page subscribes via a tiny client-side script and reloads itself when the change matches the page's source file. Result: edit a note and the corresponding browser page updates within a few hundred milliseconds.

## Scope
- **In scope:**
  - File watcher built on `watchdog` observing the configured docs root recursively.
  - Single SSE endpoint at `/events`. Each connected browser holds a long-lived response.
  - Broadcast on file create/modify/delete: `event: file-changed\ndata: <relative-path>\n\n`.
  - Client-side JS snippet appended to every rendered page. Subscribes to `/events`, calls `location.reload()` if the changed path matches the current page's source.
  - Throttle: coalesce rapid bursts of changes (editor saves often emit several events per save).
  - Graceful disconnect handling — the SSE handler tolerates client closes without hanging the server.
- **Out of scope:**
  - WebSocket-based bidirectional channel (SSE is enough; WebSocket only matters when we add the terminal panel — FEAT-0003).
  - Differential page updates (the soft-reload picks up edits without partial-update complexity).
  - Real-time index regeneration optimisation (rebuild on change is fine for typical project-os repo sizes).

## Acceptance
- Edit `docs/ARCHITECTURE.md` in an external editor; the open browser tab on `/docs/ARCHITECTURE.md` reloads within ~500 ms of the editor saving.
- Edit a different file; the page on the unrelated tab does NOT reload (only the affected page does).
- Tablet and Mac browsers both receive events when both have the page open.
- Closing the browser tab cleanly disconnects the SSE channel without server-side errors.

## Notes
SSE is the right choice over WebSocket for this scope: simpler, browser auto-reconnects, no library dependency. WebSocket comes back into play with the terminal feature (FEAT-0003) — at that point we may share the same channel for both file events and terminal IO, or keep them separate.

**Status: done (2026-05-08)** — landed across TASK-0005 (file watcher + EventBus) and TASK-0006 (SSE channel + client soft-reload). All four acceptance criteria above are met. See [[CHG-20260507-File-Watcher]], [[CHG-20260508-SSE-Live-Reload]] for the landing trail.

The shared `EventBus` and the SSE infrastructure are also the foundation for TASK-0011 (cockpit JS-side re-fetch on file events), which will extend the event payload with a typed `kind` to distinguish frontmatter vs body vs base changes.
