---
type: "[[issue]]"
id: ISS-0161
aliases: ["ISS-0161"]
title: "Replaying the backlog makes xterm answer capability queries into the live shell, and zsh reads the reply as ESC — the keymap goes vi and `k` becomes up"
status: "fixed"
owner: user:edwin
created: 2026-08-13
updated: "2026-08-13"
source: ["Edwin 2026-08-13: 'the cli still does not seem to take any keystroke input for the other terminals' … 'it seem the k key is up' … 'I can get out of the death key situation by pressing enter'"]
severity: high
component: desktop-terminal
parent: ""
related: ["[[ISS-0154-Existing-Terminals-Lose-Keyboard-Input-After-Workspace-Switch]]", "[[ISS-0160-A-Stale-Mouse-Mode-Types-Escape-Sequences-Into-The-CLI]]", "[[ISS-0016-Embedded-Terminal-Content-Runs-Off-Screen-And-Mouse-Scroll-Stops-Working-After-Switching-To-The-Console]]", "[[FEAT-0003-Embedded-Terminal]]"]
tests: []
---

# The backlog replay makes xterm answer questions nobody asked

## Problem

`attachTerminalTo` replays a 256 KB ring buffer of raw PTY output into xterm so the previous screen resumes in place. That buffer contains whatever the app wrote — **including its terminal-capability queries**: Device Attributes, DSR, OSC colour requests.

Replaying a query makes xterm **answer it again**, and an answer is written to the PTY. The program running *now* never asked. A shell reads `ESC [ ? 1 ; 2 c` as an `ESC` followed by letters, and zsh's ZLE goes to **vi command mode**, where `k` is up, `j` is down, `g` is top, `l` is right — and `Enter` is the way out.

Reported key for key: *"the up key worked … the g seems to do something different and the l"*, then *"it seem the k key is up"*, then *"I can get out of the death key situation by pressing enter."*

## Why it looked like the keyboard was dead

It never was. tmux — the ground truth beneath the pane — had the keystrokes all along:

```
project-os-dev %  hhhh          → zsh: command not found: hhhh
your-health %     ksksklks      → zsh: command not found: ksksklks
your-applications.com % ksdkkdkdkd → zsh: command not found: ksdkkdkdkd
```

The keys arrived, were interpreted as vi motions, and produced nothing visible. Typing that works and is invisible reads exactly like typing that does not work.

## Fix

Suppress everything xterm emits **for the duration of the replay**, at the data boundary rather than by filtering the backlog. A filter would need a list of reply-provoking sequences, and that list is wrong the first time a terminal gains a new query; muting the mouth catches every one, including the ones nobody has thought of. The cost is any keystroke typed during the replay window — milliseconds — which is the right trade against injecting an `ESC` into a running shell.

## Three wrong turns, recorded because they cost the afternoon

1. **A frozen interceptor read as a negative result.** `contextBridge` freezes the exposed API, so `window.cockpit.terminal.write = spy` silently did nothing. Three probes reported *"no keystrokes emitted"* and every one was measuring nothing. The finding only appeared after hooking `term.onData` directly, which cannot be frozen out.
2. **[[ISS-0160]] fitted the symptom and was not the cause.** The mouse-motion flood was real, measured and removed — and the symptom survived it. A mechanism that explains the evidence is not the same as the mechanism that produced it.
3. **The alternate screen was never corrupt.** Stripping `\e[?1049h` from the replay changed nothing, because tmux enters the alternate screen itself on every client start — measured in the live stream: `\e[?1049h \e[22;0;0t \e[?1h \e= \e[H \e[2J …`. That change was reverted.

The pattern in all three: reasoning about who *might* have sent a byte, when the bytes were available to read the whole time.

## Evidence

After the fix, on the build in the app, xterm's visible buffer and `tmux capture-pane` agree line for line on the same workspace — the prompt, the typed text, and the shell's reply to it.
