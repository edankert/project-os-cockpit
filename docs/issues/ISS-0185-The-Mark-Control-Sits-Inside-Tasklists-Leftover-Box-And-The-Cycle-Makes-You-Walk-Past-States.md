---
type: "[[issue]]"
id: ISS-0185
aliases: ["ISS-0185"]
title: "The new mark control is small and sits inside tasklist's leftover indicator box, and reaching one state means writing every state before it"
status: "fixed"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
source: ["Edwin 2026-08-17, from use: 'The new checkbox is a little small and they seem to be inside another box? Also, maybe if we bring up a dialog, can we then have one dialog with all options?'"]
severity: medium
component: desktop-renderer
parent: ""
related: ["[[FEAT-0104-The-Suite-Is-The-Surface]]", "[[TASK-0435-The-Cycling-Mark-And-Its-Paired-Write]]", "[[ISS-0176-Every-Prompt-In-The-Desktop-Shell-Is-Dead]]"]
tests: []
---

# The mark control is boxed inside another box, and the cycle makes you walk past states

Both reported from use, the day the control shipped.

## 1. It is inside another box, and that box is mine to remove

`pymdownx.tasklist` does not render a bare input. It renders:

```html
<li class="task-list-item">
  <p><label class="task-list-control"><input type="checkbox" disabled/><span
     class="task-list-indicator"></span></label> …
```

`mountAcceptanceMarks` removes `input[type=checkbox]` and **leaves the `label` and its `task-list-indicator` span behind**. That span is a styled box. So the row draws my bordered button *and* tasklist's empty indicator, and Edwin sees a box inside a box.

Two further mistakes compound it:

- The control is inserted as `li.firstChild`, which puts it **before the `<p>`** — a block element — so it sits on its own line rather than inline with the check it marks.
- `.acc-mark` has a `1px` border around a glyph (`☐`, `☑`) that is **already a box outline**. A border around a box character is a box inside a box even with nothing else on the row.

## 2. The cycle makes you write states you do not want

`[ ]` → `[x]` → `[~]` → `[F]` → `[ ]`, one write per click. So marking an unwalked check as **failed** takes three clicks, **three writes to the file**, and two dialogs you have to fill in and dismiss on the way past — because `[x]` and `[~]` each prompt.

The cycling design came from Edwin's own earlier preference (*"I actually like the cycling checkbox idea better"*), and it was the right call for a two-or-three state mark. At four states with two of them requiring justification it inverts: the intermediate states are not stops on the way somewhere, they are **writes to the record that mean something specific and false**.

## Expected

1. The `label.task-list-control` is removed with its input, not left behind, and the control sits **inline in the row's first paragraph**.
2. No border on a glyph that is already an outline; large enough to hit.
3. **One dialog, all four options.** Click the mark → a dialog naming the check, offering Pass / Could not run / Failed / Clear with one reason field, and refusing the two that need a reason without one. One click, one write.

## Notes

The reason field must stay a single field shared by the options rather than one per option: the reason belongs to the *verdict being recorded*, and three fields would let two of them hold text that is never written.

Nothing about the vocabulary changes — `~` and `F` and their grammar are settled ([[FEAT-0104]]). This is the affordance only.

## Fixed 2026-08-17

**The box inside a box was three things at once**, and all three were mine:

1. `mountAcceptanceMarks` removed `input[type=checkbox]` and left `label.task-list-control` — and its `task-list-indicator` span — standing. The whole label goes now.
2. The control was inserted at `li.firstChild`, which is the `<p>`. A block element, so the control sat on its own line above the check it marked. It mounts inside the paragraph.
3. `.acc-mark` had a `1px` border around `☐`, a glyph that is already a box outline. No border at all now; the glyphs are rings (`○ ● ◍ ✕`) at `1.35em`, and weight and colour carry the state. `ul.task-list li[data-check]` also drops its list marker, which had been reserving space for the box that is gone.

**The cycle is replaced by one dialog** naming the check, with four choices and one shared reason field:

```
1.6.14  PRO seat transfer survives reinstall
  [ Passed            ]  [ Could not run     ]
    clears the gate         clears the gate — needs a reason
  [ Failed            ]  [ Not walked        ]
    keeps blocking …        keeps blocking, and clears any reason
  [ Cancel ]
```

The state the check is already in is outlined, so a reader can see where they are before choosing where to go. The two choices that clear or hold the gate without evidence are refused without a reason **in the dialog as well as at the server**, so the reader is told before the round trip rather than after it.

**One click, one write.** Reaching `[F]` from `[ ]` cost three clicks, three writes and two prompts under the cycle; the intermediate marks were not steps toward anywhere, they were assertions that were specific and false. Cancel writes nothing and does not even repaint.

Six mutations, each chosen to defeat a guard rather than confirm one, all killed: restore the input-only removal, remount before the paragraph, restore the border, let a reasonless verdict through, make `clear` demand a reason, and move the write above the cancel check.

## Found while fixing this: the tests were pinned to a file you were using

Closing this broke `test_gate_delta.py` twice, and neither break was a defect. `../your-trainer`'s suite moved at 09:42 because **Edwin was clicking the new control** — one check went from unwalked to walked, and the gate read 59 blocking instead of 60.

A test asserting `== 60` fails exactly when the feature under test is used successfully. That is the worst available failure signal, and it was the **third** time in one session that a number read out of a living file broke something:

| reading | what moved it |
| --- | --- |
| 542 rendered boxes | the file was mid-edit when I read it ([[ISS-0184]], withdrawn) |
| 60 blocking / 13 new | Edwin marked a check from the app |
| 6 of 37 post-release boxes | the Tick button this phase shipped |

Ten assertions across the three new test files now pin **relationships** instead: the split accounts for every blocking row and loses none, no row appears in two groups, stale rows are disjoint from blocking ones, the notice's number equals the rows it could not stamp, every chronic row's release count agrees with where its tag sits in history, and the summary matches a shape rather than a value.

**The dated figures stay in the notes**, which is where a measurement belongs — [[FEAT-0108]] and the phase note record what the corpus said on 2026-08-16 and say so. A test is for what must always be true.

**One exception, deliberate:** the two corrupt store XMLs are still named individually. If Edwin repairs them that test fails, and the correct response is to delete the assertion rather than widen it — the finding will have been acted on, which is the point.
