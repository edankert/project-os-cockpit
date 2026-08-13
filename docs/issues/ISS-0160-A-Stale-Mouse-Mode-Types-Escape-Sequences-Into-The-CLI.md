---
type: "[[issue]]"
id: ISS-0160
aliases: ["ISS-0160"]
title: "A re-asserted mouse mode types escape sequences into the CLI on every mouse movement — the agent goes modal and `g` and `l` stop being letters"
status: "fixed"
owner: user:edwin
created: 2026-08-13
updated: 2026-08-13
source: ["Edwin 2026-08-13: 'the cli still does not seem to take any keystroke input for the other terminals' → 'it seems like the up key worked and it nearly looked some keys had a different assignment, the g seems to do something different and the l for instance … it is strange behaviour'"]
severity: high
component: desktop-terminal
parent: ""
related: ["[[ISS-0016-Embedded-Terminal-Content-Runs-Off-Screen-And-Mouse-Scroll-Stops-Working-After-Switching-To-The-Console]]", "[[ISS-0154-Existing-Terminals-Lose-Keyboard-Input-After-Workspace-Switch]]", "[[FEAT-0003-Embedded-Terminal]]"]
tests: []
---

# A stale mouse mode types escape sequences into the CLI

## Problem

`attachTerminalTo` snapshots each workspace's xterm mouse-tracking mode on the way out and **re-asserts it** on the way back in — [[ISS-0016]]'s fix, which restored wheel scrolling after a workspace switch. Its own comment records the flaw it accepted:

> *"if the app exited to a plain shell in this same PTY while we were detached, we'll briefly re-assert the stale tracking mode until the next redraw disables it — recoverable, and rare."*

It is not rare, and it is not recoverable by the reader, because the reader cannot see what is happening.

With the mode at `any` — DEC 1003, *report every motion* — xterm writes `\e[<35;col;row M` into the PTY **every time the mouse moves across the terminal**. If the app underneath is no longer in mouse mode, it does not receive a mouse report. It receives `ESC`, then `[`, `<`, digits, `;`, `M`.

An `ESC` into a vi-mode readline or a full-screen TUI switches it to **command mode**. From there `g` and `l` are motions rather than letters, and the arrow keys still work — which is exactly, and specifically, what was reported.

## Measured, 2026-08-13

Instrumented both directions of the live terminal and recorded a real session:

```
xterm mouseTrackingMode : any
saved per workspace     : 470ba4e2=any, a2defdd4=none, b512867a=none, …
outbound events         : 507 characters, 84 escape/mouse sequences
sample                  : "\e[<35;132;33M"  "\e[<35;181;34M"  "\e[<35;211;35M"
```

Button 35 is *motion with no button held*. Nobody clicked; the pointer merely crossed the pane.

## What this is not

It is **not** [[ISS-0154]], which was fixed the same day and is real: the console genuinely did not get the keyboard back after a switch. That fix landed and was verified. This is the defect underneath it, and it explains why the symptom survived: the keystrokes were arriving all along and being *interpreted*, because the mouse had already put the app into a mode nobody asked for.

Three probes during this investigation reported "no keystrokes emitted" and every one of them was measuring nothing — `contextBridge` freezes the exposed API, so the interceptor never installed. The finding came only after hooking `term.onData` directly, which cannot be frozen out. Recorded because a silent no-op reads exactly like a negative result.

## Fix — option 1, chosen by Edwin

Stop re-asserting the saved mode. Let the forced SIGWINCH prompt the app to re-enable its own mouse mode, which is the app's business and the only party that knows the truth.

This is the option [[ISS-0016]] rejected, and it is available now for a reason that did not exist then: [[ISS-0154]]'s fix routes every attach through `attachAndFocusTerminal`, which forces a genuine refit *after* the attach completes. ISS-0016's resize raced ahead of the reset, so the redraw could not be relied on; it no longer does.

**The risk is honest**: if an app does not re-enable mouse mode on redraw, wheel scrolling stays dead until it does. That is the trade — a scroll that needs one keypress to wake, against a terminal that silently retypes your mouse movements into a running agent.

## Fixed — 2026-08-13

The re-assert is gone, and the snapshot went with it: `workspaceMouseMode` and `MOUSE_TRACK_DECSET` existed only to feed it, so once nothing read them they were state written on every switch and consulted by nobody — [[ISS-0139]]'s class, removed alongside the code that needed it.

**Verified on the live app across A → B → A:**

```
mouse mode on A            : any     ← the app enabled it
after switching to B       : none    ← reset cleared it; nothing re-asserted
after switching back to A  : any     ← the app re-enabled it ITSELF
sequences emitted          : \e[?1;2c  \e[>0;276;0c  OSC 10/11 colour replies
```

The third line is the whole bet of option 1 and it holds: the mode returns because the app asks for it on redraw. The emitted sequences are xterm *answering* the app's Device-Attributes and colour queries — which is itself evidence the redraw fired — and there is not one `\e[<35;…M` motion report among them.

`test_the_terminal_never_re_asserts_a_mouse_mode` keeps both halves out: the DECSET table and the snapshot map.

## Correction — 2026-08-13: real mechanism, not the reported cause

Edwin, after the fix shipped and the app was restarted: *"it is not working."*

So the mouse flood was **a** defect, measured and removed, but it was not what stops the CLI taking input. This note's title quotes the symptom and should not have: the two were joined by a plausible mechanism and by the specific keys named (`g`, `l`, arrows), which fitted a modal app well enough that I stopped looking.

What is verified stays verified — no mode is re-asserted, the app re-enables its own on redraw, no motion reports reach the PTY. What is **not** established is that this was ever the reader's problem. The symptom is still open and its cause is unknown; when it is found it gets its own note rather than being appended here, because two defects sharing one title is how the second one goes missing.
