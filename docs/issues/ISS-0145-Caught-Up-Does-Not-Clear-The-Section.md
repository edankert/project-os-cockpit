---
type: "[[issue]]"
id: ISS-0145
aliases: ["ISS-0145"]
title: "Caught up does not clear the section it heads — the obligations half stays, which was a deliberate decision and is now overruled"
status: fixed
severity: medium
owner: user:edwin
created: 2026-08-11
updated: 2026-08-11
phase: "[[PHASE-030-Obligations-Go-Home]]"
features: ["[[FEAT-0071-Since-You-Looked]]"]
tasks: []
related: ["[[ISS-0134]]", "[[ISS-0144]]", "[[FEAT-0092]]"]
tags: [issue, ux, reversal]
---

# Caught up does not clear the section

## What was asked for

Edwin, 2026-08-11: *"I think this should clear the since you looked section fully instead. The Change notes or any other notes that need a follow up should not be a reason to keep this section open."*

## This reverses a decision rather than fixing a mistake

[[ISS-0134]] asked the same button to work and was answered by **re-rendering the band instead of removing it**, on this reasoning, which is still in the code:

> *"Removing the band showed the reader a dismissal that had not happened: the obligations half came straight back on the next paint, unchanged … Re-rendering shows the truth — the news is gone, what is owed remains."*

That is a good argument and it lost to a better one. **The band's subject is *since you looked*.** What is owed is not news; it did not happen while you were away, and it has a home of its own — the badges, and now the view landing pages ([[FEAT-0092]]). Keeping obligations in a band headed *"Since this cockpit first ran"* files them under the wrong sentence, and makes a dismissal control that cannot dismiss.

The half that made the old answer necessary is being removed rather than argued with: the obligations half moves out of the digest entirely.

## The fix

- `Caught up` **removes the band**. The watermark still moves on `computed_at`, not on the click, so nothing that landed while it was on screen is marked seen.
- The band no longer carries the obligations half at all, so there is nothing to come back on the next paint — which is what made removal dishonest in [[ISS-0134]]'s answer.
- The line explaining that *"Caught up covers what changed, not what is owed"* goes with it. It was a caption for a design that no longer exists.

## What the tests hold

- The band's payload no longer feeds an obligations half; what is owed is the registry's, in one place.
- After `Caught up`, `.digest-band` is absent from the DOM — asserted against the built bundle, since "it re-renders instead" is exactly the shape that passed the old test.
