# Plan — FEAT-0032 Agents screen

1. **TASK-0150.** Fleet state proxy in main: `agents:fleet` IPC returning, per workspace, the poller's coarse state plus (when a sidecar is live) the `/api/cockpit/state` snapshot (session, cost, queue via dispatch list). Cache 5s; reuse sidecar url map, not `.cockpit/url` files.
2. **TASK-0151.** `~agents` virtual page: fleet rows, aggregate header (burn, active count, 5h/7d rate budget), jump actions; move the sessions-feed entry point here; register rail + inbox-header links. Depends on TASK-0150.
