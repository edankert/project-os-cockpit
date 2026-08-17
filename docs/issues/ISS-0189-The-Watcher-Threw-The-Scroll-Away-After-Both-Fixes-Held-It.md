---
type: "[[issue]]"
id: ISS-0189
aliases: ["ISS-0189"]
title: "The file-changed watcher re-navigated 150ms after every write and discarded the scroll both earlier fixes had held"
status: "fixed"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
source: ["Edwin 2026-08-17: 'The file still jumps after coming out of the dialog, can we not somehow update the file in memory and then do a save in the background without re-loading?'"]
severity: medium
component: desktop-renderer
parent: ""
related: ["[[ISS-0187-The-Repaint-Loses-Your-Place-A-Refusal-Is-Silent-And-The-Dialog-Has-No-Save]]", "[[ISS-0188-The-Scroll-Fix-Looked-Right-Passed-A-Guard-And-Did-Nothing]]"]
tests: []
---

# The watcher threw the scroll away after both fixes held it

## The cause, and why two fixes missed it

Writing a mark changes the file. The sidecar's watcher notices, emits `file-changed`, and the client runs:

```ts
softReloadTimer = window.setTimeout(() => {
  …
  void navigateTo(currentRel, { replace: true });   // no keepScroll
}, 150);
```

`applyScrollTarget` then takes its `fromHistory === false` branch and sets `scrollTop = 0`.

So both earlier attempts were **correct in the path they touched and irrelevant**. [[ISS-0187]] held the scroll around `repaintDoc`; [[ISS-0188]] moved that into the animation frame where it could not be overwritten. Both worked. Then, 150 milliseconds later, a completely different code path re-rendered the document and sent the reader to the top.

Three rounds on one symptom, and the first two never touched the thing causing it. What they had in common is that each was diagnosed from the code path I had just written, rather than from *everything that runs when a file changes*.

## The fix Edwin proposed, which is the right one

> *"can we not somehow update the file in memory and then do a save in the background without re-loading?"*

Yes — and the reason a reload was there at all no longer holds. It existed because an HTML checkbox shows two states and the vocabulary has six, so the row could not be patched to the truth. **This control draws its own mark**, so it can simply be redrawn.

So a successful write patches the row and re-navigates nothing:

- the row's HTML comes back **from the server**, rendered through the one markdown pipeline — building it in the client would make the client a second writer of the verdict grammar, which is the drift this project keeps paying for
- `data-mark` is updated and the control redrawn from it
- the incoming `file-changed` for **our own write** is suppressed, because letting the watcher re-navigate would undo the patch

## And the watcher holds the scroll regardless

Separately from marks: a file changing under an open document is not a reason to move the reader to the top of it. That is true for an edit made in another editor too, and it has presumably been mildly annoying for as long as live reload has existed.

## Expected

1. Marking a check does not re-render the document at all.
2. The watcher's own re-render holds the reader's position.
3. A guard covers the *watcher* path, not just the paths already fixed — the failure here was that two guards passed while a third path was broken.

## Fixed 2026-08-17

**Marking a check re-renders nothing.** The write returns the row as it now renders — from the server, through the one markdown pipeline — and the client swaps that row's contents, updates `data-mark`, and redraws the control. The `file-changed` for our own write is suppressed for 1.2s so the watcher cannot undo it.

**And the watcher holds the reader's place regardless**, which matters beyond marks: a file changing under an open document is not a reason to move someone to the top of it, and that has been true of every edit made in another editor for as long as live reload has existed.

Five mutations, all killed, including one that restores the exact `navigateTo` without `keepScroll` that caused this.

### Two of the five survived first, and it is the same shape a third time

`row_html` was checked as *named* in the client and *keyed* in the response — and a mutation that fetched it and then discarded it (`void rowHtml`), and another that returned `""` for it, both passed. Two ends, no wire.

That is now three occurrences in one session: a node created but never appended, a held scroll passed but never wired through, and a rendered row fetched but never applied. The lesson is specific enough to state as a rule — **a guard on a value must assert the value is used, not that its name appears** — and general enough that it will keep recurring until it is written somewhere the next person reads.

### Why this took three rounds

[[ISS-0187]] held the scroll around the repaint. [[ISS-0188]] moved that inside the animation frame so it could not be overwritten. Both were correct in the path they touched. **Neither touched the watcher**, which re-rendered 150ms later.

Each round was diagnosed from the code path I had just written rather than from everything that runs when a file changes. The tell was there each time — Edwin reported the same symptom unchanged — and I took the repetition as *the fix did not land* rather than *the diagnosis is wrong*.

### Two things the fix surfaced, both caught by tests already here

**`repaintDoc` became dead code** the moment its only caller stopped re-navigating, and `test_the_renderer_has_no_unreachable_top_level_function` said so. Deleted, along with the two guards describing how it held its scroll — a guard about a mechanism that no longer exists is worse than no guard, because it reads as coverage.

**`_rendered_row` swallowed every exception.** A test stub missing `resolve` produced an `AttributeError` that became `""`, which the client treats as *row not found* and silently leaves the prose alone. A rendering failure and a missing row are different things and looked identical. The except is narrow and logged now, and still non-fatal: the write has already happened and must not be reported as failed.

The stub also taught the test something true: with nothing resolving, `[[ISS-0277]]` renders as an **unresolved** wikilink that keeps its literal text — correct behaviour, and it made the first version of the assertion wrong. The stub resolves what the corpus would, so the test exercises the real path.
