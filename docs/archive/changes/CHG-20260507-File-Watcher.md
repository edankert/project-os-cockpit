---
type: "[[change]]"
id: CHG-20260507-File-Watcher
aliases: ["CHG-20260507-File-Watcher"]
title: "File watcher + EventBus — index now stays in sync with the docs tree"
status: merged
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
source: ["[[TASK-0005]]"]
commit: ""
pr: ""
impacts:
  - "src/docs_server/events.py"
  - "src/docs_server/watcher.py"
  - "src/docs_server/index.py"
  - "src/docs_server/server.py"
issues: []
features: ["[[FEAT-0002]]"]
related: ["[[REQ-0004]]", "[[TASK-0006]]", "[[TASK-0011]]"]
---

# File watcher online

## Summary
Adds a watchdog-based filesystem watcher that publishes `FileEvent`s onto a shared in-process `EventBus`. The index subscribes and re-indexes any `.md` path on the fly, so wikilink resolution, type counts, and `/index/<plural>` listings reflect filesystem state without a server restart. The bus also becomes the foundation for the SSE channel (TASK-0006) and the cockpit's JS-side re-fetch (TASK-0011).

## Impact

### New modules / behaviour
- `src/docs_server/events.py` — `FileEvent` dataclass + `EventBus` (lock-protected fanout, snapshot-then-dispatch so slow subscribers don't block new subscriptions). Also: `relative_to_ci` / `is_under_ci` path helpers (see "macOS gotcha" below).
- `src/docs_server/watcher.py` — `Watcher` wraps `watchdog.observers.Observer`; the inner `_Handler` dispatches `FileSystemEvent`s through `_emit` which deduplicates per-`(path, kind)` within a 100 ms debounce window. `Moved` events are split into `delete`+`create` so consumers don't have to special-case rename.
- `src/docs_server/index.py` — new `Index.subscribe_to(bus)` registers a `.md`-only invalidation callback that calls `update_path(...)` on every event. `update_path` re-reads the file (or removes the record if the file is gone).
- `src/docs_server/server.py` — `DocsServer.__init__` instantiates `EventBus` + `Watcher`; `run()` starts the watcher and stops it in a `finally` block.

### macOS gotcha (and fix)
APFS / HFS+ volumes are *case-preserving but case-insensitive*. fsevents always reports paths with their on-disk case (`/Users/Edwin/...`), but `$(pwd)` returns whatever case the user typed when they `cd`'d (often `/Users/edwin/...`). Python's `Path.relative_to` and string comparison are case-sensitive — so events were being silently dropped because the path didn't match the stored docs root. Fix: a small `relative_to_ci` helper folds case for the prefix check; watcher uses it for event filtering, and index uses it for `_is_excluded`, `_index_path`, and `url_for`. `Index.update_path` also walks records case-insensitively when removing a stale entry before re-indexing.

### Lifecycle / shutdown
The watcher's Observer thread is a daemon; the HTTP server's worker threads are daemons. `KeyboardInterrupt` under interactive Ctrl+C goes through the `run()` `finally` and stops the watcher cleanly. Programmatic SIGINT from a sandboxed harness may not always propagate, but daemon threads ensure the process still dies.

## Follow-ups
- [ ] [[TASK-0006]] — SSE endpoint at `/events` subscribes to the same bus and broadcasts `event: file-changed\ndata: <rel-path>\n\n` to connected browsers; rendered pages add a small `<script>` that listens and reloads when their source path matches.
- [ ] [[TASK-0011]] — extend `FileEvent` with a typed `kind` for cockpit re-fetch granularity (`frontmatter` vs `body` vs `base`). The current event payload is intentionally coarse so TASK-0006 can land first against today's primitives.
- [ ] Acceptance test (`TST-*`) for live index updates — currently smoke-verified manually (FEAT count 6 → 7 → 6 on create/delete cycle).
