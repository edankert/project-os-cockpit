---
type: "[[issue]]"
id: ISS-0081
aliases: ["ISS-0081"]
title: "xterm's right-click word-select combined with unconditional copy-on-select to overwrite the clipboard with the word under the cursor, so right-click-to-paste pasted that word back"
status: fixed
severity: medium
phase: "[[PHASE-020-Clipboard-That-Works]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["Edwin 2026-07-30, minutes after ISS-0080 shipped: 'when I use the right click to copy it only copies the current word'"]
component: desktop-renderer
related: ["[[ISS-0080-Console-Context-Menu-Replaced-By-Terminal-Convention]]"]
fixed_by: ["[[TASK-0263-Terminal-Copy-And-Paste]]"]
tests: []
---

# Right-click clobbered the clipboard it was about to paste

## What

`rightClickSelectsWord` makes xterm select the word under the cursor on a right-click, and on macOS it defaults to **on**.

[[ISS-0080]] made copy-on-select unconditional and right-click the paste gesture. The two compose into a loop:

```
right-click → xterm selects the word under the cursor
            → onSelectionChange fires
            → copy-on-select writes that word to the clipboard
            → pasteIntoTerminal reads the clipboard
            → the word is pasted back
```

So right-click appeared to "copy the current word", and whatever you had actually copied was gone.

## Cause

Introduced by [[ISS-0080]], not present before it: copy-on-select used to be opt-in and defaulting to off, so the word-select was harmless. Turning it on made a dormant default load-bearing.

**A default that was never wrong before is not a default that was checked.** I enabled copy-on-select and did not look at what else already reacted to a selection changing.

## Fixed 2026-07-30

`rightClickSelectsWord: false`. Right-click is the paste gesture and must not touch the selection at all.

Verified: after a right-click, `term.hasSelection()` is false and a clipboard sentinel written beforehand is still there.

```
rightClickSelectsWord     : false
selection after right-click: null
clipboard intact          : true
```

Guarded and mutation-verified by flipping it back.

## Notes

Third report in this sequence, and the third time the fix for one thing exposed the next. Worth reading the three together — [[ISS-0079]], [[ISS-0080]], this — as one lesson: each fix was correct for the case it addressed and changed the conditions for a neighbouring one, and none of the three was found by a test.
