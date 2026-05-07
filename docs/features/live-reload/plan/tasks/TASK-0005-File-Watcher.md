---
type: "[[task]]"
id: TASK-0005
aliases: ["TASK-0005"]
title: "File watcher (watchdog) emitting change events"
status: done
phase: "[[PHASE-001-MVP]]"
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
source: []
implements: ["[[FEAT-0002]]", "[[REQ-0004]]"]
fixes: []
effort: S
due: ""
depends: ["[[TASK-0001]]"]
blocks: ["[[TASK-0006]]"]
related: []
tests: []
---

# File watcher

## Definition of Done
- [x] `watcher.py` watches the configured docs root recursively via `watchdog.observers.Observer`.
- [x] Emits `FileEvent(kind, rel_path, abs_path)` with `kind ∈ {created, modified, deleted}` (moves are split into delete+create) on the shared `EventBus` from `events.py`.
- [x] Per-`(path, kind)` debounce of 100 ms drops the burst of redundant events that editor saves emit.
- [x] Index subscribes via `Index.subscribe_to(bus)` and re-indexes the affected path on every `.md` event; non-`.md` events are ignored at the subscriber, not the watcher (so the SSE channel and cockpit re-fetch in TASK-0011 see all events).
- [x] Watcher's Observer thread is a daemon — process shutdown isn't blocked by the watcher even if `stop()` is missed. `Watcher.stop()` joins with a 2 s timeout.

## Steps
- [x] `events.py`: new module with `EventBus` (lock-protected fanout, snapshot-then-dispatch so slow subscribers don't block new subscriptions) and the `relative_to_ci` / `is_under_ci` case-insensitive path helpers (see Notes).
- [x] `watcher.py`: `Watcher` wraps `Observer`; `_Handler(FileSystemEventHandler)` publishes onto the bus. Atomic-rename writes (vim, etc.) come through as `Moved` and are split into delete+create so consumers don't have to special-case them.
- [x] `index.py`: `Index.subscribe_to(bus)` registers a `.md`-only invalidation callback that calls `update_path(...)`.
- [x] `server.py`: `DocsServer` owns the bus + the watcher; `run()` starts the watcher inside a `try/finally` that calls `watcher.stop()` on exit.
- [x] Smoke-tested: create/modify/delete cycles in the docs tree update the in-memory index live (`/index/features` count goes 6 → 7 → 6 within ~600 ms).

## Notes
The bus is shared between this watcher and the SSE channel (TASK-0006). Keep the bus thread-safe and lock-free where possible.

**macOS path-case bug discovered + fixed:** APFS volumes are case-preserving but case-insensitive, so `$(pwd)` can resolve to `/Users/edwin/...` while fsevents reports `/Users/Edwin/...` for the same directory. Python's `Path.relative_to` is case-sensitive and was silently dropping every event. Fix: `events.relative_to_ci` does a case-insensitive prefix match; both watcher and index use it. Also fixed `Index.update_path` to find existing records case-insensitively before re-indexing, so a stale uppercase-keyed record can't shadow a new lowercase-keyed one.

**Shutdown caveat:** under interactive Ctrl+C the server shuts down cleanly (the `KeyboardInterrupt` path in `run()` calls `watcher.stop()` via `finally`). When SIGINT is delivered programmatically from a sandboxed scripting harness it sometimes doesn't propagate to the main thread; in that case the daemon Observer + `daemon_threads=True` on `ThreadingHTTPServer` still let the process die, just less gracefully. Not a real-world issue.
