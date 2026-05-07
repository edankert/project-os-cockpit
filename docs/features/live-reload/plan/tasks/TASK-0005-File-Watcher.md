---
type: "[[task]]"
id: TASK-0005
aliases: ["TASK-0005"]
title: "File watcher (watchdog) emitting change events"
status: backlog
phase: "[[PHASE-001-MVP]]"
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
source: []
implements: ["[[FEAT-0002]]", "[[REQ-0004]]"]
fixes: []
effort: S
due: ""
depends: [TASK-0001]
blocks: [TASK-0006]
related: []
tests: []
---

# File watcher

## Definition of Done
- [ ] `watcher.py` watches the configured docs root recursively using `watchdog`.
- [ ] Emits change events (`created` / `modified` / `deleted`) with the relative path on a thread-safe queue / event bus.
- [ ] Coalesces bursts (editor-save events fire several handlers per save) — debounce window ~100 ms per path.
- [ ] Invalidates the wikilink/ID index entry for the changed file (or rebuilds the affected slice).
- [ ] Survives clean process shutdown (no zombie threads).

## Steps
- [ ] Add a `EventBus` class with `subscribe(callback)` / `publish(event)`.
- [ ] `watchdog` `Observer` with a custom `FileSystemEventHandler` that publishes onto the bus.
- [ ] Index invalidation hooks: index module subscribes to the bus and updates entries.
- [ ] Debounce: small `defaultdict[path, last_event_time]` with a 100 ms threshold.
- [ ] Smoke-test: print events to stdout when files change.

## Notes
The bus is shared between this watcher and the SSE channel (TASK-0006). Keep the bus thread-safe and lock-free where possible.
