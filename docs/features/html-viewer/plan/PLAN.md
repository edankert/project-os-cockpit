---
type: "[[plan]]"
title: "Plan — one HTML viewer"
status: draft
owner: user:edwin
created: 2026-09-12
updated: 2026-09-12
source: ["[[FEAT-0148-One-HTML-Viewer]]"]
implements: ["[[FEAT-0148-One-HTML-Viewer]]"]
related: ["[[FEAT-0147-Pictures-Beside-The-Note]]", "[[PHASE-042-A-Note-Shows-What-It-Is-About]]"]
---

# Plan — one HTML viewer

## Delivery sequence

1. **Build the viewer beside the bench** ([[TASK-0613-A-Generic-HTML-Viewer]]). Both exist for one commit. This is deliberate: removing a surface and building its replacement in the same diff means there is no moment at which either can be checked on its own.
2. **Re-point the links** ([[TASK-0614-Links-Stop-Asking-For-The-Bench]]) and supersede [[REQ-0062-A-Link-That-Names-A-Design-Opens-The-Design-Bench]]. Needs Edwin's answer on reading (a) or (b) — see that requirement's Approval section.
3. **Intent** ([[TASK-0616-Intent-After-The-Bench]]) — designs stay reachable from where they are reachable today.
4. **Remove the bench** ([[TASK-0615-Remove-The-Bench]]), its endpoints and its ~198 tests. Nothing before this has removed anything, so up to here every step is reversible by deletion rather than by restoration.
5. **Register and Deck** ([[TASK-0617-Register-And-Deck]]), in the same commit as the removal per CLAUDE.md.

## Dependencies

- **Hard:** [[ADR-0042-What-May-Be-Framed]] accepted, and [[TASK-0609-An-HTML-Page-May-Show-A-File-Beside-It]] landed, before the viewer is built — the viewer inherits one path rule (inside `docs_root`, no traversal) rather than inventing a second one.
- **Hard:** [[TASK-0611-Upstream-The-Markdown-First-Contract]] — the authoring skill flipped upstream — before [[TASK-0615-Remove-The-Bench]]. Otherwise every repo's agents keep authoring for a surface that is gone.
- **Soft:** step 4 after step 3, so that nothing is unreachable even for one commit.

## Open questions

- **Should the viewer be a new route at all**, or `/docs/<rel>` with the artifact header set? [[ADR-0042-What-May-Be-Framed]] removed the only thing that distinguished them, so the answer may be that one route serves both and only the headers differ. [[TASK-0613-A-Generic-HTML-Viewer]] decides and records it.

- ~~Does a design's ID open its note, or the viewer on its page?~~ **Answered 2026-09-12: the note.** The rule is deleted rather than re-pointed; `designBenchTarget` and the design-register fetch go, and the route guards and parked-link handling stay because they are about links generally. [[TASK-0614-Links-Stop-Asking-For-The-Bench]].
- ~~Which bench capabilities are re-homed and which retired?~~ **Answered 2026-09-12**, after Edwin corrected two rows of the table: design Accept/Decline are kept on the note (they were never the bench's), the verdict's revision binding is retired with [[RISK-0009-A-Design-Verdict-Stops-Naming-What-It-Judged]] carrying the hazard, and region comments are retired with what is given up stated honestly.
- **Does anything replace region-anchored commenting?** The plan says no, on 12 comments by one reviewer on one note. If the answer is yes, it is a separate feature and it should have a case.
- **What does the viewer do with a note that has more than one page?** No note in the fleet has one today. Recommend: list them and let the reader pick, rather than guessing.
- **`## Revisions` after capture is removed.** The log is written by hand from then on. Should the authoring skill say so, or should something prompt for it at commit time? The former is one sentence; the latter is a hook and a new obligation.
