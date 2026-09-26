---
type: "[[task]]"
id: TASK-0308
aliases: ["TASK-0308"]
title: "Annotations under the design's desk entry, degrading honestly"
status: done
phase: "[[PHASE-025-Design-Before-Code]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[FEAT-0069-Annotate-To-Request]]"]
parent: "[[FEAT-0069-Annotate-To-Request]]"
effort: S
depends: ["[[TASK-0307]]"]
blocks: []
related: []
tests: []
---

# Annotations under the design's desk entry, degrading honestly

## Definition of Done

- Annotations list under the design's queue entry with their anchors re-resolved at render; a lost anchor says `anchor lost at revision <sha>` — never floats to the wrong spot.
- Resolution through the existing resolve endpoint.

## Done — 2026-08-11

`resolve_anchor` re-finds an annotation in the design **as it stands now**, and reports which of three states it is in — weakest claim last:

| state | meaning |
|---|---|
| `found` | the quote is still in the design — the strongest evidence the commented thing survived, and independent of any structure |
| `moved` | the quote is gone but the variant it named still exists — still about a present shape, exact spot lost |
| `lost` | neither survives |

**Never floats to the wrong spot**, which is the DoD's rule and the reason the states are distinct: a comment silently re-attached to different content is **worse** than one that admits it is lost, because the reader trusts it and it is about something else.

Resolution prefers the quote over the variant deliberately — a quote surviving inside a *renamed* variant is still evidence the content survived, and reporting that as lost would throw away a good anchor on a cosmetic change.
