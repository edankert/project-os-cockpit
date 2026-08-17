---
type: "[[issue]]"
id: ISS-0188
aliases: ["ISS-0188"]
title: "The scroll fix ran a frame too early and was overwritten by requestAnimationFrame — it looked right, passed a guard, and did nothing"
status: "fixed"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
source: ["Edwin 2026-08-17: 'The file still jumps to the top after exiting the dialog the other issues are fixed.'"]
severity: medium
component: desktop-renderer
parent: ""
related: ["[[ISS-0187-The-Repaint-Loses-Your-Place-A-Refusal-Is-Silent-And-The-Dialog-Has-No-Save]]"]
tests: []
---

# The fix looked right, passed a guard, and did nothing

## What was wrong with the fix

[[ISS-0187]] item 1 was closed with this:

```ts
const held = docView.scrollTop;
await navigateTo(currentRel, { replace: true });
docView.scrollTop = held;
```

Which is the obvious shape and is wrong, because `applyScrollTarget` **defers its own scroll to `requestAnimationFrame`**:

```ts
requestAnimationFrame(() => {
  …
  if (fromHistory) docView.scrollTop = scrollPositions.get(pathOnly) ?? 0;
  else             docView.scrollTop = 0;          // <- one frame later
});
```

So the restore ran synchronously, the frame ran afterwards, and set it to zero. The reader still landed at the top.

## The part that matters more than the bug

**The guard passed.** `test_the_repaint_holds_the_scroll_position` asserted that `repaintDoc` reads `docView.scrollTop`, that the read precedes the `navigateTo`, and that the write follows it. Every one of those was true. The behaviour was still broken, because the assertion was about the **shape of the source** and the defect was about **when a callback runs**.

That is a whole class this repo cannot currently reach. Every renderer test here is a Python scan of `renderer.ts` — there is no DOM, no `requestAnimationFrame`, no JS test runner in `desktop/package.json` at all. A source scan can check that a mechanism is *present*; it cannot check that nothing later undoes it.

It is also the fourth guard this session that could pass for a reason unrelated to the thing it names — after one that compared two CSS rules including their selectors, one that grepped for a string its own prose contained, and one that checked a node was created rather than appended.

## Expected

1. The held position is handed to `navigateTo` and honoured **inside** the frame, ahead of both existing branches and ahead of a fragment — a repaint is not a navigation and the reader has not asked to go anywhere.
2. The guard targets that mechanism rather than the shape, and **forbids the broken pattern** — assigning `docView.scrollTop` immediately after an awaited `navigateTo` — anywhere in the file.
3. The gap itself is recorded rather than papered over: see the note below.

## The gap this leaves, named and not closed

**There is no way to behaviourally test the renderer in this repo.** Adding one — a DOM harness, or enabling `--remote-debugging-port` so the running app can be driven — is a real piece of work with real consequences (the second changes the app's security posture), and it is not something to do as a side effect of a scroll fix.

Until then, renderer behaviour is verified by a person using it, which is how all four of these rounds were caught. That is worth saying out loud rather than letting a green suite imply otherwise.

## Fixed 2026-08-17

The held position is a parameter now, honoured **inside** the frame:

```ts
await navigateTo(currentRel, { replace: true, keepScroll: docView.scrollTop });
…
requestAnimationFrame(() => {
  if (keepScroll !== undefined) { docView.scrollTop = keepScroll; return; }
  if (frag) { … }
  …
});
```

Ahead of the fragment branch as well as the `= 0` one: a repaint is not a navigation, and the reader has not asked to go anywhere.

### The guards, and the one that survived

Four mutations, all killed, and **the first of them restores the exact code that shipped broken** — so this specific regression cannot come back quietly:

```
killed  back to the synchronous restore that did nothing
killed  keepScroll honoured AFTER the frag branch
killed  keepScroll never reaches applyScrollTarget
killed  repaintDoc stops passing it
```

The third **survived the first attempt**, and for the same reason as a mutation two rounds ago: the guards checked that `repaintDoc` passes a held position and that `applyScrollTarget` honours one, and said nothing about whether the value travels between them. Two ends and no middle — which is the same shape as asserting a node is created and never that it is appended.

A file-wide guard now also forbids the broken pattern itself: `docView.scrollTop = …` within a few lines of an awaited `navigateTo`, anywhere. The next person to want that will reach for exactly that shape.

### What is still not verifiable here

**Nothing above proves the behaviour.** These are source assertions, the defect was about *when a callback runs*, and this repo has no DOM harness and no JS test runner. The gap is recorded in the section above and left open deliberately: closing it means either a DOM harness or enabling remote debugging on the app, and neither belongs inside a scroll fix.

Edwin found all four rounds of this by using it, which is currently the only thing that can find them.
