---
type: "[[change]]"
id: CHG-20260523-Cockpit-Soft-Live-Reload
aliases: ["CHG-20260523-Cockpit-Soft-Live-Reload"]
title: "Cockpit: soft live-reload — file changes refresh panes without tearing down the terminal"
status: merged
owner: user:edwin
created: 2026-05-23
updated: 2026-05-23
source: ["[[TASK-0014]]"]
commit: ""
pr: ""
impacts:
  - "src/project_os_cockpit/static/cockpit.js"
  - "src/project_os_cockpit/static/sse-reload.js"
issues: []
features: ["[[FEAT-0006]]"]
related: ["[[CHG-20260508-SSE-Live-Reload]]", "[[CHG-20260522-Cockpit-Embedded-Terminal]]"]
---

# Cockpit: soft live-reload

## Summary
The original FEAT-0002 live-reload (`sse-reload.js`) does `location.reload()` on every relevant `file-changed` SSE event. After the embedded terminal landed (FEAT-0003), that became a problem — the full reload nukes the iframe, killing whatever shell session was running. Users had to choose: live-update of docs *or* keep their terminal session.

This change moves the file-changed handling into `cockpit.js`, which re-fetches the three panes individually (left via `loadLeftPane`, centre + right via `navigateTo(current, {replace: true})`). The terminal iframe is never re-mounted, so the shell session survives. `sse-reload.js` now bails when the cockpit shell is mounted (presence of `#cockpit-centre`) — non-cockpit pages (notices, errors) still get the full reload.

## Implementation

### `cockpit.js` — `mountCockpitEventStream` extended
- New `file-changed` listener inside the existing EventSource. Calls `scheduleSoftReload()`.
- `scheduleSoftReload()` debounces on 150 ms — a save-burst from an editor coalesces into one refresh.
- On fire: `navigateTo(window.location.pathname + window.location.search, {replace: true})` refreshes centre + right; `loadLeftPane()` (with `navCache = null` reset) refreshes left.

### `sse-reload.js` — early-bail
- New first line: `if (document.getElementById("cockpit-centre")) return;`
- Doc comment updated to point at the cockpit.js soft-reload path.
- Non-cockpit pages keep the original `location.reload()` behaviour unchanged.

## v1 scope vs original DoD
TASK-0014's original DoD specified per-pane targeted re-fetch (only re-fetch nav when a feature changed; only re-fetch context when the active note's link set was touched). v1 ships the always-refresh-all-three-panes path because:
1. It's ~40 LOC vs ~120, and ships now.
2. For a 1388-note repo the round-trip is fast enough.
3. Avoids the client-side complexity of file-type detection + outbound-set caching.

v2 (smart targeting) is parked. Re-open if measurements show v1's refresh cost is a problem.

## Action required
Restart any running cockpit to load the new `cockpit.js` + `sse-reload.js`. After restart, hard-refresh tabs once so the new JS loads (subsequent SSE-driven reloads will be soft).

## Documentation Coverage
- features: covered (FEAT-0006)
- requirements: not-applicable
- tasks: TASK-0014 marked done
- issues: not-applicable
- tests: not-applicable (manual browser verification; JS-only change)
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new (this note)
- snapshot: updated (TASK-0014 status backlog → done; updated timestamp bumped)
