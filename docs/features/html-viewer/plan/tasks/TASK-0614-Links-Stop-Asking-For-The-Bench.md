---
type: "[[task]]"
id: TASK-0614
aliases: ["TASK-0614"]
title: "The design-ID link rule is removed: a design's ID opens its note like every other ID, and REQ-0062 is superseded rather than rewritten"
status: done
phase: "[[PHASE-042-A-Note-Shows-What-It-Is-About]]"
owner: user:edwin
created: 2026-09-12
updated: 2026-09-12
source: ["Edwin, 2026-09-12, answering REQ-0064's Approval question: the note", "[[REQ-0064-One-Viewer-And-One-Rule-About-What-May-Be-Framed]]"]
parent: "[[FEAT-0148-One-HTML-Viewer]]"
effort: M
depends: ["[[TASK-0613-A-Generic-HTML-Viewer]]"]
blocks: ["[[TASK-0615-Remove-The-Bench]]"]
related: ["[[REQ-0062-A-Link-That-Names-A-Design-Opens-The-Design-Bench]]", "[[FEAT-0146-A-Link-That-Names-A-Design-Opens-The-Design-Bench]]"]
tests: ["[[TST-0087-An-HTML-Page-Opens-In-The-Viewer]]"]
tags: [task, links, supersession]
---

# The link rule is removed

## The decision this task carries out

**Decided by Edwin, 2026-09-12: the note.** A design's ID opens its note, exactly like every other ID in the system. There is no special case and no successor rule — the rule is deleted, not re-pointed. A design's HTML page, when it has one, is reached from the note.

The first version of this task was written for a choice that had not been made, and listed the alternative — re-point the rule at the viewer — as reading (b). That option is closed. The reason the note won is the same reason the whole phase exists: once a design is Markdown with pictures, the note **is** the design, so an ID resolving to the note is not a fallback, it is the right answer.

## Definition of Done

- [x] `designBenchTarget` is deleted from `desktop/src/renderer/deep-link.ts`.
- [x] `locateAndOpen` in `renderer.ts` no longer asks it, and no longer fetches the design register to resolve a link.
- [x] The four routes FEAT-0146's independent review found breakable — `cockpit://` links, cross-repo `[[project#ID]]` links, and either parked across a project switch — still reach `locateAndOpen` with the link's ID. **Keep the guards that pin this.** They exist because four one-line breaks to those routes passed every test; they are about link resolution generally, not about designs, and they survive the rule they were written alongside.
- [x] The parked-link handling from [[ISS-0298-A-Parked-Link-Opens-In-Whichever-Project-Arrives-First]] is untouched — it is not design-specific and its defect predates the design rule.
- [x] [[REQ-0062-A-Link-That-Names-A-Design-Opens-The-Design-Bench]] is `superseded`, `superseded_by: "[[REQ-0064-One-Viewer-And-One-Rule-About-What-May-Be-Framed]]"`. Its six acceptance criteria stay ticked as written; they were true when written and the note records that, not today's behaviour.
- [x] [[FEAT-0146-A-Link-That-Names-A-Design-Opens-The-Design-Bench]] is `superseded`, `superseded_by: "[[FEAT-0148-One-HTML-Viewer]]"`. `done -> superseded` is the allowed transition (`STATUSES.md` `[[feature]]`).
- [x] `TST-0084` and `TST-0085` are `retired`, not deleted.
- [x] The question the snapshot focus has been carrying since 2026-09-11 — *should an in-repo `[[DES-####]]` wikilink open the bench too?* — is answered in the record as **no, and there is no bench**, and the focus note stops carrying it.
- [x] `tests/test_design_links.py` (7 tests) goes with the rule.

## Steps

- [x] Delete the rule; keep the route guards. Those two things are easy to remove together by accident.
- [x] Set the four statuses. Do **not** edit FEAT-0146's or REQ-0062's prose to describe today's behaviour — a superseded note describes what was true when it was written.

## Notes

Superseding work that landed the previous day looks like churn and is not. FEAT-0146 solved something real: a link to a design opened the project and not the page. The general fix is that a design's page is reachable from its note like everything else, which makes the special case unnecessary rather than wrong. Both steps belong in the record.

## Outcome (2026-09-12)

The rule is gone: `designBenchTarget` is deleted from `deep-link.ts` with its nine node cases, and `locateAndOpen` no longer fetches a register to resolve a link (`designsForLink` went with it). A design's ID opens its note.

**The guards under the rule were kept and re-homed.** Four tests moved from `tests/test_design_links.py` into `tests/test_cross_repo_links.py`, which is where link behaviour is pinned: every route still reaching `locateAndOpen` with the link's ID, a parked link consumed only by the project it names ([[ISS-0298-A-Parked-Link-Opens-In-Whichever-Project-Arrives-First]]), a reply from a project the reader left never landing, and a project switch forgetting the previous project's designs. Three of the four came out of FEAT-0146's independent review and none of them belonged to the rule. `test_design_links.py` is deleted.

One clause did belong to it and was rewritten rather than dropped: the argument-order check asserted `designBenchTarget(noteId,` and now asserts that `locateAndOpen` looks up `noteId`. Swapping two string arguments still builds and still passes everything else, which is what that clause is for.

**Four statuses set, no prose rewritten.** [[FEAT-0146-A-Link-That-Names-A-Design-Opens-The-Design-Bench]] `superseded` by FEAT-0148, [[REQ-0062-A-Link-That-Names-A-Design-Opens-The-Design-Bench]] `superseded` by REQ-0064 with its six criteria left ticked as written, [[TST-0084-A-Design-ID-Opens-The-Bench-And-Other-IDs-Open-Their-Note]] and [[TST-0085-A-Link-To-A-Design-Shows-The-Design]] `retired` with a line saying what they checked and when. Each keeps describing what was true on 2026-09-11.

**The open question is answered in the record.** *Should an in-repo `[[DES-####]]` wikilink open the bench too?* — **no, and there is no bench.** It is written at the top of FEAT-0146, and the snapshot's focus note stops carrying it.
