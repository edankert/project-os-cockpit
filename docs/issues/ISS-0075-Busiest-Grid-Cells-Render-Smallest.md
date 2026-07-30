---
type: "[[issue]]"
id: ISS-0075
aliases: ["ISS-0075"]
title: "The contribution grid's busiest days render 33% smaller than its quietest — the 'second channel' was subtractive, so the strongest signal was the weakest mark"
status: fixed
severity: medium
phase: "[[PHASE-018-History-You-Can-Reach-And-Traverse]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["Edwin 2026-07-30, on sight: 'Why do the days with most changes look different then the others (they look smaller)?'"]
component: desktop-renderer
related: ["[[TASK-0259-Contribution-Grid]]", "[[DES-0004-Attention-In-The-Squares]]"]
fixed_by: ["[[TASK-0259-Contribution-Grid]]"]
tests: []
---

# The busiest cells are the smallest

## Measured

Every cell is 9×9. The intensity steps carry an **inset** `box-shadow` in the *background* colour, growing with the step:

```
step 1   9×9   opacity 0.3   shadow none
step 2   9×9   opacity 0.5   inset 0.5px  rgb(28,28,28)
step 3   9×9   opacity 0.75  inset 1px    rgb(28,28,28)
step 4   9×9   opacity 1     inset 1.5px  rgb(28,28,28)
```

An inset shadow in the background colour is a border drawn **inside** the box. So the visible coloured core is:

```
step 1   9px      step 4   9 − 1.5×2 = 6px
```

**The busiest day renders a third smaller than the quietest.** And the two channels fight: step 4 is darkest but smallest, step 1 is lightest but biggest, so the size partially cancels the intensity it was meant to reinforce.

## Why I built it

I added the ring citing [[DES-0004]]'s rule that colour must not be the only channel, and wrote in [[TASK-0259]] that "five shades of one hue is the encoding DES-0004 refused for the phase squares".

**That misreads the rule.** DES-0004's problem was **hue** — the phase squares already spent colour on *type*, so a second meaning could not use colour at all. A contribution grid spends nothing else on colour, and it varies **lightness**, not hue. Lightness survives greyscale by definition and is unaffected by every common colour-vision deficiency; it is precisely why GitHub's scale is accessible.

So the second channel was solving a problem that did not exist — and it was implemented subtractively, which made it actively harmful.

## Expected

Intensity reads monotonically: busier is darker, and every cell is the same size.

## Next Actions

- [x] Drop the inset ring; opacity alone
- [x] Check `empty` stays distinguishable from step 1, which is the one distinction lightness alone has to carry
- [x] Guard the monotonicity, not the specific values

## Notes

Found on sight, in seconds, by the person the grid was built for. The suite could not see it: the cells are 9×9 by every measurement a test would make, and the defect lives entirely in what is painted inside that box.

That is the eighth finding this week from someone looking at a rendered surface. This one is the sharpest, because the mistake was **citing a design rule I had helped write, to justify the opposite of what it says**.


## Fixed 2026-07-30

The ring is gone. Opacity alone: `0.28 / 0.5 / 0.75 / 1`.

Re-measured in the running app — every cell 9×9, `boxShadow: none` at every step, opacity strictly increasing. The busiest day is now the darkest *and* the same size as every other.

`empty` stays distinguishable: it is `--row-hover` (`rgb(42,45,49)`) against step 1's green composited to roughly `rgb(55,71,66)` — about 20 levels of luma apart in greyscale, which is the one distinction lightness alone has to carry and it carries it.

### Guarded on the property, not the pixels

`intensity is monotonic and no step shrinks the cell` parses the built CSS and asserts two things: **no step carries an `inset` shadow**, and **opacity strictly increases**. Mutation-verified by restoring the 1.5px inset on step 4.

Deliberately not asserting the specific opacities — those are taste, and a guard that pins taste gets deleted the first time someone adjusts it. What must not change is that busier reads stronger and nothing subtracts from a cell.

### The lesson

The suite could not have caught this. Every cell **is** 9×9 by any measurement a test would take; the defect lives entirely in what is painted inside that box, and only an eye sees it.

What the suite could have caught — and what the guard now does — is the *mechanism*: an inset shadow in the background colour, on a cell whose size is meant to be constant. That is the difference between guarding an appearance and guarding a property.

**The worst part is the reasoning, not the CSS.** I cited [[DES-0004]] — a design note I wrote — to justify adding a channel, and got its rule backwards. It says hue cannot carry a second meaning *when hue is already spent*. It does not say lightness needs help. Citing a rule from memory instead of re-reading it produced a confident, documented, wrong decision, and the comment I left made it look considered.
