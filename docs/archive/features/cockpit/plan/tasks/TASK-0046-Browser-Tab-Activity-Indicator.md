---
type: "[[task]]"
id: TASK-0046
aliases: ["TASK-0046"]
title: "Cockpit: browser tab activity indicator (title + favicon dot when hidden)"
status: cancelled
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-22
updated: 2026-07-20
source: []
parent: "[[FEAT-0006]]"
fixes: []
effort: XS
due: ""
depends: []
blocks: []
related: ["[[TASK-0044]]"]
tests: []
---

# TASK-0046 — Browser tab activity indicator

## Goal
When the project-os-cockpit browser tab is in the background and the cockpit observes activity (file watcher event from the existing SSE channel), update the document title (prepend `● `) and swap the favicon to a dotted variant so the user notices on the OS tab strip. Clear when the tab regains focus.

## Definition of Done
- [ ] Document title gains a `● ` prefix when activity is detected while the tab is hidden.
- [ ] Favicon swaps to an alternate (dotted) variant under the same condition. Revert to default favicon on focus.
- [ ] Indicator clears when `document.visibilitychange` fires with `visible`.
- [ ] No effect when the tab is already visible (foreground use is unchanged).
- [ ] No effect on systems without favicon support — graceful degradation.

## Steps
- [ ] Add an alternate favicon (`favicon-dot.svg`) in `static/`. Single dot in the corner of the existing mark.
- [ ] JS module (small, hooked into `sse-reload.js` or a new sibling): listen to the existing SSE event stream + `document.visibilitychange`. Maintain an `unread` flag.
- [ ] On each SSE message while `document.hidden`: set `unread = true`, update title + swap favicon `<link rel="icon">` href.
- [ ] On visibility change to visible: clear `unread`, reset title + favicon.

## Notes
- **v1 signal**: file-watcher SSE — captures any LLM CLI / editor action that touches a `.md`. Close enough to "agent returned an answer" for the common case.
- **v2 enhancement** (separate task — easier now that TASK-0047 landed): postMessage bridge inside the proxied ttyd iframe. xterm.js `onData` → `parent.postMessage({type:"terminal:data"})` → cockpit fires the indicator on actual terminal output, not just file changes. Strictly better signal than the v1 file-watcher proxy.
- Independent of TASK-0043/0044 — works the moment a file is edited, with or without the embedded terminal.

## Cancelled (2026-07-20)

Obsolete: the browser-tab activity indicator (title `●` prefix + favicon dot for a hidden tab) was designed for the browser-served cockpit. The desktop Electron shell — now the primary surface — already delivers this signal natively and better via the rail dots (busy / needs-input pulse) and OS notifications (FEAT-0020). A favicon dot would be a strictly weaker duplicate, so this is cancelled rather than built.
