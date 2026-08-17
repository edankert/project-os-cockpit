---
type: "[[task]]"
id: TASK-0435
aliases: ["TASK-0435"]
title: "The cycling mark and its paired write — one click advances the mark and writes it, and Confirm pairs the exception with its justification in the release note"
status: done
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["Edwin 2026-08-16: 'I actually like the cycling checkbox idea better'", "Edwin 2026-08-16: 'it would be great if I could provide this information directly while selecting the ! for the check'"]
parent: ""
origin: "[[FEAT-0104-The-Suite-Is-The-Surface]]"
effort: L
depends: ["[[ISS-0175-The-Nth-Checkbox-Is-Not-The-Nth-Task-Line]]", "[[TASK-0434-The-Check-Map-And-The-Exception-Mark]]"]
blocks: ["[[TASK-0436-An-Undocumented-Exception-Is-Owed]]"]
related: ["[[ADR-0022]]"]
tests: ["[[TST-0031-The-Exception-Mark-And-Its-Justification]]"]
---

# The cycling mark and its paired write

## The interaction

`[ ]` → `[x]` → `[!]` → `[ ]`, one click each, and **the mark is written on every click**. Screen and file never disagree, which is how ticking already behaves.

Landing on `[!]` opens a justification field inline. **Confirm** writes the entry into the `preparing` release note. Clicking *past* `[!]` writes no entry and leaves none.

## Why the gesture is not gated

The objection to cycling was never mis-clicks — those 542 checkboxes have been one click each since the suite was first rendered. It was the **undo path**: correcting a mis-tick is the commonest act in the document, and the cycle routes it through the exception state.

Gating the gesture would have made the ordinary case worse. Instead the incomplete state is made loud ([[TASK-0436]]): an exception nobody has justified is counted and named until somebody writes the reason.

## Definition of done

- [x] One click advances the mark and writes it; the file matches the screen after every click
- [x] Confirm on the justification field writes an `## Exceptions` entry naming the check, the reason, the actor and the date
- [x] **Release note first, then nothing else to undo** — the mark is already written, so a failed note write leaves an unjustified exception, which is the state [[TASK-0436]] reports rather than a corruption
- [x] Clicking past `[!]` to `[ ]` removes any entry that existed for it — the release has not shipped, so nothing was claimed
- [x] `[!]` is refused when no release is `preparing`, with a reason the surface shows: an exception is *from a release*
- [x] The write is addressed by section-and-ordinal with a name check and an `mtime` guard ([[TASK-0430]])
- [x] Loopback-only, and enumerated by the existing guard
- [x] Walked by hand against a throwaway suite, driving the real control


## Blocked 2026-08-16

Waiting on [[ISS-0175]]. The interaction is keyed on which rendered checkbox is which check, and that correspondence does not hold: `your-trainer` parses 579 checks and renders 542 inputs. A control wired to DOM position would write to the wrong check, which is worse than no control.


## Deferred 2026-08-16, with [[FEAT-0104]]

[[ISS-0175]] is fixed and its cause is known, but the half that blocks this is not a cockpit bug: where a task list opens with no blank line those checks have **no checkbox to click**, so no interaction can be keyed on them. The remedy is a blank line in the suite, which belongs to the repo that owns it.


## Re-homed to [[PHASE-999]] on 2026-08-16

[[PHASE-034]] closed and this is parked, not resolved — `deferred` is not a resolved status, so carrying it inside a closing phase would fire `PHASE-CHILDREN` and, worse, would let a closed phase claim work it did not do. The sentinel is where work without a concrete delivery phase lives. Its origin and its reasoning stay above.

## Done 2026-08-17 — with `~`/`F` instead of `!`, and the real blocker found

The cycle is `[ ]` → `[x]` → `[~]` → `[F]` → `[ ]`, each click writing immediately, and `[~]`/`[F]` refused without a reason. `[!]` is never offered: measured across the fleet it is written in **zero** suites while `~` and `F` are the record's own, and Edwin's call was *"I have no problem using ~ instead."*

**The blocker this task was deferred for was not the blocker.** The note said [[ISS-0175]] — rows with no rendered checkbox. That is real and accounts for six of `your-trainer`'s 579 rows. The actual obstruction was that **`pymdownx.tasklist` only understands two marks**: a `[~]` or `[F]` row renders with no input element at all, so an HTML checkbox can never carry four states and the alignment guard trips for the whole document. `AcceptanceMarkTreeprocessor` stamps the **list item** instead, above tasklist in priority order, so all four marks are addressed and the client draws one control for them.

Re-marking **replaces** the verdict rather than stacking it, and cycling back to `[ ]` takes the justification with it — a row cannot claim both that nobody walked it and that somebody decided why it could not be walked.
