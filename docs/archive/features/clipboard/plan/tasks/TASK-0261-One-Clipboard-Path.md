---
type: "[[task]]"
id: TASK-0261
aliases: ["TASK-0261"]
title: "One clipboard path through the main process, and no silent failures"
status: done
phase: "[[PHASE-020-Clipboard-That-Works]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["[[FEAT-0054-Clipboard-That-Works]]"]
parent: "[[FEAT-0054-Clipboard-That-Works]]"
effort: S
depends: []
blocks: ["[[TASK-0263-Terminal-Copy-And-Paste]]"]
related: []
tests: []
---

# One clipboard path

## Definition of Done
- [x] `clipboard.read()` / `clipboard.write()` IPC, backed by Electron's main-process `clipboard` module
- [x] All five `navigator.clipboard` call sites in the renderer converted; **none left**
- [x] Every write reports success or failure to its caller — no `void`-ing a promise
- [x] A failed copy shows a status line
- [x] Reads and writes work with the window unfocused

## Steps
- [x] `registerClipboardIpc()` beside the other IPC modules
- [x] A renderer helper `copyText(text, label)` that writes, and on failure shows the status
- [x] Convert: copy-on-select, terminal copy, terminal paste, copy-path (×2)
- [x] Test: the IPC round-trips, and a guard that `navigator.clipboard` is gone from the renderer

## Notes

`navigator.clipboard.writeText` throws `NotAllowedError: Document is not focused`, and `readText` additionally needs the `clipboard-read` permission. Electron's main-process `clipboard` needs neither, and the renderer already talks to main for everything else.

**The silence is the worse half.** Five call sites, every one `void`-ed or bare-caught, so a copy that did not happen looked exactly like one that did — which is how this survived long enough to be reported by a user rather than noticed.

## Done 2026-07-30

`desktop/src/ipc/clipboard.ts` + `cockpit.clipboard.{read,write}`. All five renderer call sites converted; `navigator.clipboard` appears nowhere in the built renderer except in the comment explaining why.

**Writes are read back before being reported successful.** A silent no-op is the failure mode this task exists to remove, so trusting `clipboard.writeText()` to have worked would have reproduced it one layer down.

**Both IPC calls resolve with a result rather than rejecting**, so a caller cannot drop a failure by forgetting to `await` — which is how all five sites went wrong.

`copyText(text, label)` in the renderer shows a status on failure. Copy-on-select stays quiet on success (it fires on every drag; a status line per drag is noise) and speaks on failure.

Verified live: `write` then `read` round-tripped with the window unfocused, which is where `navigator.clipboard` threw `NotAllowedError`.
