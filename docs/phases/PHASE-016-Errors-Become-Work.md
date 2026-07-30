---
type: "[[phase]]"
id: PHASE-016
aliases: ["PHASE-016"]
title: "Errors become work — a validator result is either being fixed now or filed as an issue, never a number nobody can act on"
status: done
order: 16
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
goal: "A validator error stops being a permanent count on a badge. While a session is running it is a row in that session's work list that closes when the agent fixes it; if it is still standing when the session ends, it becomes a real issue with an ID and goes to the Issues view."
features:
  - "[[FEAT-0051-Validator-Errors-As-Session-Work]]"
requirements: []
issues: []
depends: ["[[PHASE-013-Fleet-Surfaces]]"]
related: ["[[FEAT-0018-Verification-Health-Surface]]", "[[FEAT-0028-Fleet-Health-Surface]]", "[[TASK-0250-Fleet-Badge-On-The-Rail]]", "[[ISS-0065-Record-Column-Lost-Its-Source]]"]
tags: [validation, agents]
---

# Errors become work

## Where this came from

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
