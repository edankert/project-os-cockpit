---
type: "[[phase]]"
id: PHASE-016
aliases: ["PHASE-016"]
title: "The overview answers questions — every number on it leads somewhere, and every thing on it says what it is"
status: done
order: 16
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
goal: "Turn the overview from a page of numbers into a page of answers: a validator count becomes work you can watch drain, the history band becomes documents rather than a git log, that history becomes reachable and traversable, and everything on the page says which item it is."
features:
  - "[[FEAT-0051-Validator-Errors-As-Session-Work]]"
  - "[[FEAT-0052-History-Timeline]]"
  - "[[FEAT-0053-History-Navigation]]"
requirements: []
issues:
  - "[[ISS-0075-Busiest-Grid-Cells-Render-Smallest]]"
  - "[[ISS-0076-Phase-Rows-Do-Not-Show-Their-Phase-Id]]"
  - "[[ISS-0077-Phase-Granularity-Collapsed-To-One-Per-Request]]"
supersedes: ["[[PHASE-017-History-As-Document-Events]]", "[[PHASE-018-History-You-Can-Reach-And-Traverse]]", "[[PHASE-019-Overview-Legibility]]"]
depends: ["[[PHASE-013-Fleet-Surfaces]]"]
related: ["[[FEAT-0018-Verification-Health-Surface]]", "[[FEAT-0028-Fleet-Health-Surface]]", "[[TASK-0250-Fleet-Badge-On-The-Rail]]", "[[ISS-0065-Record-Column-Lost-Its-Source]]"]
tags: [validation, agents]
---

# The overview answers questions

## Merged 2026-07-30 — this phase absorbed three others

Opened as **"Errors become work"** and widened to cover what turned out to be one push. [[PHASE-017]], [[PHASE-018]] and [[PHASE-019]] are `superseded` into it; their notes stay as the record of each leg.

Four phases for one afternoon's work was the drift [[ISS-0077]] measured: nine phases opened in a day against nine in the preceding twelve weeks, at a fifth of the size. Each was created reactively — one per request — because the document-first rule needs a focus item and an open phase is the cheapest way to get one.

They belong together because their goal states without listing them: **every number on the overview leads somewhere, and everything on it says what it is.** All four came from Edwin looking at the page and asking *what is this / how do I get there / why does that look wrong*.

| leg | was | what it delivered |
|---|---|---|
| errors | PHASE-016 | a validator count became rows in the session's work list, and issues at close-out |
| history | [[PHASE-017]] | the history band became document state changes, with commits as dividers |
| navigation | [[PHASE-018]] | a contribution grid whose days are destinations, and History in the rail |
| legibility | [[PHASE-019]] | the phase rows say which phase they are |

**Nothing before PHASE-013 was touched**, and [[PHASE-013]], [[PHASE-014]] and [[PHASE-015]] stay separate: planned in advance, retrospective for earlier work, and a records correction respectively.

## Where the first leg came from

Edwin, watching the rail badge [[TASK-0250]] shipped: *"I noticed the project image showed some error overlays during the changes but it was very difficult for me to understand what these errors were related to."*

Reproduced: creating one note mid-session produced `METRICS` (the summary is one count behind) and `PHASE-CHILDREN` (a phase closed while a child was still open). The badge read `2`. The tooltip read `docs: 2 validator errors`. That is the entire information budget — a number, with no way to reach what it counts.

Worse, both of those were **the session's own work in progress**, and cleared themselves minutes later. The badge was correct and useless.

## The principle

**A check result is either work someone is doing, or a record. It is never a standing number.**

Edwin's framing, which replaced three worse proposals of mine: *"if they are fixed in the same session by the LLM then this should simply be shown on top of the console in the session summary... If this needs my input then it should become an actual issue and should be handled in the issues view."*

That dissolves rather than relocates the problem. A transient condition does not belong in a register — but anything that reaches the human has been **promoted into a record first**, so by the time it appears in Issues it belongs there like everything else.

## The rule that avoids a lookup table

Which errors an agent can fix and which need a person is not decided in advance. It is **measured**:

> An error still standing when the session ends needs a human.

No classification table — and this repo has scars from exactly that kind of table ([[ISS-0023]], [[ISS-0024]]: a second vocabulary drifting because nothing held it to the first). The session either fixed it or it did not, and the answer cannot be stale.

## Scope

- **[[FEAT-0051]]** — the errors reach the session panel as rows and close as they are fixed; close-out promotes the survivors.
- Promotion happens at **close-out**, not automatically (Edwin's call). The close-out step already says to run the validator and fix what it reports; filing what could not be fixed is the missing half of that sentence, not a new obligation.

## Out of Scope

- **Auto-filing issues in the background.** Considered and declined: issues appearing without anyone asking is a worse failure than one occasionally missed, and close-out is where the check already runs.
- **Changing what the validator checks.** Nothing here alters a rule; it changes where the result is shown.
- **Other repos' surfaces.** The rail badge keeps its current meaning for repos with no live session — which this phase makes *stronger*, see below.

## Exit Criteria

- [x] A validator error opens a row in the session summary while a session is running — evidence: a bad note produced `COUNTER` + `METRICS` rows over SSE, heading *"Docs checks — 2 to fix"*
- [x] The row closes when the error is fixed, without a reload — evidence: deleting the note flipped both to `fixed`, heading to *"all cleared"*
- [x] Rows are reachable — evidence: clicking the `COUNTER` row navigated `~overview` → the offending note; `METRICS` is deliberately not clickable and says why
- [x] Close-out files what survives, and says so — evidence: the rule in `CLAUDE.md` (not `LIFECYCLE.md` — template-owned) plus two guards, one of which fails if the template ever adopts it
- [x] Nothing is filed twice — evidence: dedup on `(code, subject)`, stated in the rule and guarded

## Notes

**The badge gets sharper, not redundant.** For a project with no live session nobody is typing, so anything the badge shows has already survived a session by definition. It stops meaning "something might be mid-edit" and starts meaning "this project has something nobody is fixing" — which is worth a mark on the rail.

**Three of my proposals were wrong before this one was right.** The Issues page (a register cannot hold a self-clearing condition), the Needs-you panel (every row there means an agent is blocked on you; a stale count is not that, and it would rebuild the section [[ISS-0068]] deleted three days ago), and a split-the-count scheme that needed a classification table. Recorded because the useful pattern is the one Edwin applied: ask *who fixes this*, not *how long does it last*.


## Closed 2026-07-30

[[FEAT-0051]] done, all three tasks, every criterion verified against the running app with real induced errors rather than synthetic payloads.

**The design is Edwin's and it is better than the three I proposed.** Mine were: the Issues page (wrong — a register cannot hold a self-clearing condition), the Needs-you panel (wrong — every row there means an agent is blocked on you, and it would have rebuilt what [[ISS-0068]] deleted three days earlier), and a split-the-count scheme that needed a classification table this repo has twice been burned by.

His question was different: **not "how long does it last" but "who fixes it"**. That reframing dissolves the problem instead of relocating it, because anything reaching the human is *promoted into a record first* and so belongs in Issues legitimately.

**And the classification falls out of it rather than being added.** An error still standing when the session ends needs a human — measured, not guessed, and impossible to have stale.

### Worth carrying forward

The reporter was the user, looking at a badge I had shipped that afternoon and finding it unreadable. Everything about it was technically correct: the count was right, the tooltip was accurate, the SSE was live. It was **useless**, because it answered *how many* and the only question anyone has is *what*.

That is the fifth finding this week that came from someone looking at a rendered surface rather than from a check — after [[ISS-0069]], [[ISS-0072]], [[ISS-0073]] and [[ISS-0074]]. Four of the five were mine to have noticed and I did not, because I verified that each surface *worked* rather than that it *answered anything*.


## Closed 2026-07-30 — merged, then closed

All three features done ([[FEAT-0051]], [[FEAT-0052]], [[FEAT-0053]]), all three issues fixed ([[ISS-0075]], [[ISS-0076]], [[ISS-0077]]), fourteen items.

Against the widened goal — *every number on the overview leads somewhere, and everything on it says what it is*:

- **A validator count leads somewhere** — rows in the session's work list that close as they are fixed, and issues at close-out for what survives.
- **The history band is documents** — status transitions as rows, commits as dividers, replacing three tiles that each made git the subject.
- **History is reachable** — a rail button, and a contribution grid whose days are destinations.
- **Everything says what it is** — phase rows carry their ID.

Every one of the four came from Edwin looking at the page and asking *what is this / how do I get there / why does that look wrong*. None came from a check.

### The shape of the day

This phase exists in its current form because [[ISS-0077]] counted: nine phases opened on 2026-07-30 against nine in the preceding twelve weeks, at a fifth of the size. Four of them were this one push. The merge was the cleanup; the rule in `CLAUDE.md` and `project-os-dev` ISS-0029 are what stop it recurring.
