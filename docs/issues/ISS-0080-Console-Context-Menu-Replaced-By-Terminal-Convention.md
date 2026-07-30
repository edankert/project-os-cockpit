---
type: "[[issue]]"
id: ISS-0080
aliases: ["ISS-0080"]
title: "The console's context menu does not work for the user across three attempts — replace it with the terminal convention (select copies, right-click pastes) rather than debug a menu a console does not need"
status: fixed
severity: medium
phase: "[[PHASE-020-Clipboard-That-Works]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["Edwin 2026-07-30: 'I think it is a focus issue... Probably better not to have the context menu in the console and instead to use the console copy and paste directly, select and right-click and right-click to paste?'"]
component: desktop-renderer
related: ["[[FEAT-0054-Clipboard-That-Works]]", "[[TASK-0263-Terminal-Copy-And-Paste]]", "[[TASK-0167-Terminal-Context-Menu]]"]
fixed_by: ["[[TASK-0263-Terminal-Copy-And-Paste]]"]
tests: []
---

# Replace the console menu with the convention

## What

Three attempts, three reports that the console's context menu still does not copy or paste, while **⌘C / ⌘V do work**. Under measurement the menu path writes to the PTY correctly and the xterm textarea holds focus throughout — so I cannot reproduce it, and the user can reproduce it every time.

**When the measurement and the user disagree three times, the measurement is answering a different question.** Something about a real right-click — the native menu, the OS-level focus transition, the pointer capture — differs from a dispatched event, and chasing it is chasing a menu a console does not need.

## The proposal, which is better than the bug

Edwin's: **select copies, right-click pastes.** The PuTTY / mintty convention, familiar to anyone who lives in a terminal, and it removes the mechanism rather than repairing it — there is no menu to lose focus to.

It also happens to be the honest fix for a second thing: `copyOnSelect` currently defaults to **off**, so "select to copy" was not the behaviour at all unless you had found the toggle.

## What must not be lost

**`Restart console` exists only in that menu.** It is the one action with no other route — deleting the menu without rehoming it strands a genuinely useful command. `Clear` is `clear` in the shell and `Select All` is ⌘A; neither needs saving.

## Expected

- Selecting console text copies it.
- Right-clicking the console pastes.
- Restart console is reachable.
- No console context menu.

## Next Actions

- [x] Right-click pastes; delete `showTerminalMenu` and `.term-menu`
- [x] `copyOnSelect` defaults **on** — the convention requires it
- [x] Move `Restart console` into the app menu beside Toggle Terminal
- [x] Keep the copy-on-select preference reachable, or drop the preference and make it the behaviour

## Notes

**Right-click always pastes, with no selection-aware mode.** mintty and PuTTY both do this and the predictability is the point: a gesture that sometimes copies and sometimes pastes is worse than either. If you have a selection you have already copied it, because selecting is the copy.

Worth recording that the user diagnosed this correctly from the outside ("I think it is a focus issue") while three rounds of instrumentation from the inside said the mechanism worked. The instrumentation was not wrong; it was measuring a synthetic click.


## Fixed 2026-07-30

- **Right-click pastes.** `showTerminalMenu` and its five `.term-menu` CSS blocks are deleted.
- **Selecting copies**, unconditionally. `copyOnSelect` was an opt-in defaulting to **off**, so "select to copy" was never the behaviour unless you had found the toggle — half of why the console's clipboard felt broken. It is `const copyOnSelect = true` now: the convention, not a setting.
- **`Restart Console` moved to the app menu**, beside Toggle Terminal. It was the only action in the deleted menu with nowhere else to live.
- **`Clear` and `Select All` were not rehomed**: `clear` is a shell command and ⌘A is xterm's. Naming that so their absence reads as a decision.

Two guards, mutation-verified: the convention is in place (no menu, right-click pastes, copy-on-select on), and `Restart Console` survived the deletion.

### A guard was deleted, not muted

`the terminal captures its selection before the menu opens` guarded [[TASK-0263]]'s fix for a menu that no longer exists. It went red the moment the menu did. Deleting it was correct — a guard kept alive past the thing it protects gets muted, and a muted guard is worse than none.

### What I got wrong, three times

I measured the menu path writing to the PTY, measured the xterm textarea holding focus throughout, and each time concluded the mechanism worked. It did — **for a dispatched event.** A real right-click involves a native menu, an OS-level focus transition and pointer capture that `dispatchEvent` does not reproduce.

Edwin diagnosed it correctly from the outside on the first try ("I think it is a focus issue") while three rounds of instrumentation from the inside said otherwise. The lesson is not that the instrumentation lied — it is that **a synthetic event is not the interaction**, and when a user reports the same thing three times, the thing to change is the mechanism, not the measurement.


## Copy-on-select: raised, considered, kept (Edwin, 2026-07-30)

I put the case for turning it back off and Edwin chose to keep it. Recorded so it is not re-argued, and so anyone who later finds their clipboard overwritten finds the reasoning rather than filing a bug.

**The argument against**, which stands regardless of the decision: X11 has two clipboards — PRIMARY (written by selecting, pasted by middle-click) and CLIPBOARD (written by an explicit copy). Copy-on-select is safe there because it writes to a buffer nothing else reads. **macOS has one.** So on this platform every stray drag across terminal output silently replaces whatever was copied, and [[ISS-0081]] was that hazard firing through the right-click.

**What makes it acceptable anyway:** the gesture is deliberate, the console is where you most often want to grab a path or an error, and ⌘C remains available for the cases where you want to be explicit. The alternative — select does nothing, ⌘C copies — trades a live convenience for a risk that has now been narrowed to actual drags.

**If it does bite:** the change is one line (`const copyOnSelect = true` → a setting defaulting off) plus rehoming the toggle, since the console menu that used to carry it is gone.
