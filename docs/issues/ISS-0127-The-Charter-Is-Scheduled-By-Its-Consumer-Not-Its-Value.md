---
type: "[[issue]]"
id: ISS-0127
aliases: ["ISS-0127"]
title: "The goal was derivable from the record and the argument for writing it down did not hold — only the non-goals are worth a note, because only they leave no trace"
status: declined
phase: ""
owner: user:edwin
created: 2026-08-10
updated: "2026-08-14"
source: ["Session 2026-08-10: filed arguing the intent charter should be pulled forward; Edwin — 'Do we actually need a goal note, now the LLMs define the goal options?' — and the original argument did not survive checking"]
severity: low
component: "planning"
parent: ""
related: ["[[FEAT-0077-The-Intent-Charter]]", "[[TASK-0333-The-Charter-Note]]", "[[DES-0003-Intent-Page-And-Claims-Board]]", "[[PHASE-027-The-Standing-Worker]]", "[[REL-0001-The-Human-Has-Levers]]", "[[ISS-0125-The-Singleton-Documents-Have-No-Lifecycle-And-No-Home]]", "[[PHASE-028-Borrowed-Capability]]"]
tests: []
---

# The goal was derivable; only the non-goals are worth writing

## What this issue said first, and why it was wrong

Filed 2026-08-10 arguing that [[FEAT-0077]]'s intent charter should be pulled out of [[PHASE-027]] and written early, because nine phases were being ordered with nothing to check them against. Its central evidence was that a charter *"would have caught"* [[DES-0010]] — a design authored and superseded inside 48 hours.

**That claim does not survive checking, and it was the load-bearing one.**

What killed [[DES-0010]] were three measurements, recorded in [[ADR-0020]]: zero questions had ever been created in the repo's history; *"am I done?"* needs a count rather than a page; and the desk held two things that were not obligations while omitting the largest one there is. **None of those is an intention.** They are facts about the corpus, discovered by rendering its payload.

And the principle that replaced the design — obligations live with their subject — did not pre-date [[ADR-0020]]. It *was* [[ADR-0020]]. A charter written the week before would have contained none of it.

So what actually caught [[DES-0010]] was measuring the surface before designing further for it. The lesson is **measure before designing**, which this project already practises and already records, not *write a charter*.

## The goals are derivable, so a note restating them is duplication

The project's thesis was assembled from the record in a single pass, from [[ADR-0009]] (the principal is a role), [[ADR-0020]] (obligations live with their subject), [[DES-0003]] (*"the cockpit cannot tell a true claim from a false one"*), [[PHASE-028]] (*"the governance thesis nobody else is building"*) and [[REQ-0026]].

A charter would therefore be **a summary of notes that already exist** — the shape this repo keeps rejecting: [[ISS-0023]] (one vocabulary in eight places), [[ISS-0068]] (a list re-listing items that already have a home), one home per fact.

It would also be a ninth member of the class [[ISS-0125]] just measured as **94% stale fleet-wide**. A stale statement of intent is worse than none: it is a false claim on the most authoritative-looking page in the repo.

## What does not survive derivation

One thing, and it is the reason this issue stays open rather than being closed outright.

**Non-goals leave no trace.** What a project built is recoverable from its record; what it *deliberately did not build* produces no note, no commit, no test. [[PHASE-028]]'s *"so the cockpit's effort goes into the governance thesis nobody else is building"* is the only one written anywhere, and it is a phase goal that happens to imply a project one.

**And so do the principal's standing constraints.** *"I work one project at a time"* (Edwin, 2026-08-09) killed the fleet board, and survives only as a line inside a superseded design note. Cheap to lose, expensive to rediscover, and unknowable from the corpus.

## Suggested resolution

- **Do not write the charter**, and **leave [[FEAT-0077]] and [[TASK-0333]] in [[PHASE-027]]**. Its real consumer is delegated acceptance — an agent judging on the principal's behalf genuinely needs the asking written down, and that is a different requirement from a person wanting a goal. Scheduling it with its consumer was right after all.
- **Consider a short non-goals note instead**: what this tool must not become, plus the standing constraints the principal holds that the record cannot infer. Five lines, not five sections.
- **Test it the way the original filing proposed** — the one part of it that stands: if it never refuses a proposal, it was not worth writing, and it should be deleted rather than maintained.

## What this changes elsewhere

[[REL-0001]]'s *"The goal it serves"* section cites this issue for the claim that the charter is the goal. It is corrected to point at the record instead — the release serves a thesis the record already states, not a document that does not exist.

## Next Actions

- [x] Decide whether the non-goals note is worth five lines — no note
- [x] ~~If written, place it with the standing documents~~ — not written
- [x] Close this issue either way — closed 2026-08-14

## Declined — 2026-08-14

No non-goals note. The charter question was already settled; this closes the small remainder.
