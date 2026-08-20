# Plan — a release says what is in it

[[FEAT-0142-A-Release-Says-What-Is-In-It]], parked in [[PHASE-999-Future]]. **Not scheduled**, and deliberately not broken into tasks yet.

## Why there are no tasks

Three of the open questions in the feature note change what gets built, not merely how:

1. Where the decision is persisted before the release ships.
2. What `done` but held back means in the record.
3. Whether excluding a feature excludes its checks from the gate.

The third is the one that matters. A check gates through `covers:`, so "this feature is not in this release" and "this check does not block this release" are the same sentence read from two ends — which is [[ISS-0206]]'s subject. Breaking this into tasks before that is settled would produce a scope-selection UI whose effect on the gate nobody decided, on the surface whose whole job is to say whether a release can ship.

## The order, when it starts

1. **Answer question 3**, in the record. Probably an ADR — it is a rule about what a gate means, and [[ADR-0035]] is the kind of thing it would sit beside.
2. **The persistence decision** (question 1), which is small once 3 is settled.
3. **Server**: a third `kind` beside `derived` and `frozen`, or `derived` plus a held-back set. The distinction the page must draw is between a default and a decision, so the payload has to carry it.
4. **Client**: the contents rows gain the act, and the page says which rows are chosen.
5. **The gate**, only if 1 says it moves.

## What must not happen

**No verdict write path appears on the release page.** [[ADR-0035]] removed one and [[ISS-0210]] is the record of what it cost — sixty live marks on the page reporting the release was blocked, so the fastest way to unblock it was to tick the things saying it was blocked. Scope selection is a fact about the release and belongs to the release note. If the implementation finds itself writing to a check, the design is wrong.
