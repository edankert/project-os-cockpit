---
type: "[[adr]]"
id: ADR-0027
aliases: ["ADR-0027"]
title: "The obligation registry counts what needs a person — not only what the record owes, and not only things that are notes"
status: "accepted"
owner: user:edwin
created: 2026-08-13
updated: 2026-08-13
phase: "[[PHASE-030-Obligations-Go-Home]]"
source: ["Edwin 2026-08-13, choosing between widening the registry and running a parallel channel: 'write it up and widen the registry's definition'", "ISS-0156: the repo you have open is the one whose unpushed count is never computed"]
decision: "The registry's scope is what needs a person, not only what the record owes. An obligation's subject need not be a note. Admission is gated on four tests, and an obligation whose count can be unknown is not admissible."
alternatives: ["Keep the registry pure and run git through a parallel channel that renders identically", "Leave unpushed work out of the registry entirely", "Widen the definition (chosen)"]
consequences: ["The note-less obligation path stops being a special case and becomes the general one", "Every obligation ships a noun and a verb", "Absent-at-zero is preserved, so an unknown count is a defect rather than a state"]
supersedes: ""
superseded: ""
related: ["[[ADR-0020-Obligations-Live-With-Their-Subject]]", "[[ADR-0025]]", "[[ADR-0022]]", "[[FEAT-0089-The-Obligation-Registry-And-The-Badges]]", "[[FEAT-0100-Unpushed-Work-Needs-A-Person]]", "[[DES-0011-Publication-Is-An-Obligation]]", "[[ISS-0156-The-Open-Workspace-Is-The-One-Whose-Unpushed-Count-Is-Never-Computed]]", "[[PHASE-030-Obligations-Go-Home]]"]
tags: [adr, obligations]
---

# The registry counts what needs a person

## Context

`obligations.py` opens with its own definition: *"What the record owes a person, enumerated **by note type**."* Both halves are load-bearing and both are now in the way.

**By note type** is the module's best idea. A hand-written list of seven kinds was wrong three times in one day; enumerating over the corpus inverted the burden so that *the corpus supplies the checklist*, and a type present with no declaration fails a test. That stays.

But it means an obligation's subject is a note, and there is already one that isn't: `STANDING_OBLIGATION`, *"the one obligation whose subject is not a note (TASK-0382)"*, whose subject is a manifest entry. It is handled by **two special cases** — one bolted into `counts_by_kind()`, and a second in `_needs_you_group()` because `owed_items()` yields no rows for it. The seam has already failed once, and the code records the symptom: *"Intent's group came out 3 against a badge of 5."*

**What the record owes** is the second problem. Everything in the registry is a judgment about the record: approve, review, decide, confirm. Unpushed commits are not a judgment — they are work already judged and not yet published. Strictly read, they are what the *repository* owes, and the registry has no place for them.

That strict reading is now expensive. [[ADR-0022]] lets the delegate push to non-deploy remotes, and where it does not, **the human is the pusher of last resort** — Edwin, accepting it: *"if not pushed automatically then this should clearly be identified in the tool."* The tool's mechanism for *"this needs you"* is the registry and its badges. Keeping publication outside them means building a second mechanism that renders identically to the first.

## Decision

**The registry's scope is what needs a person.** Not only what the record owes, and not only obligations whose subject is a note.

An obligation is admissible when **all four** hold:

1. **A person must discharge it.** Not a machine under current policy. If the delegate may do it and does, it is not owed to anybody.
2. **It has a subject a surface can show.** The row points at the thing — a note, a commit, a manifest entry — because [[ADR-0020]] puts the obligation where its subject lives, and an obligation with no subject has nowhere to live.
3. **It is discharged by an action the cockpit can offer or name.** A verb, in the registry's vocabulary, shipped from the server ([[TASK-0357]]'s rule).
4. **It is countable, and its count is never unknown.** See below — this is the test that does the most work.

The fourth is the boundary that stops a widened definition becoming a notification centre. *"Something is a bit off"* is not an obligation; *"three commits are unpushed"* is.

**A note-less obligation is no longer a special case.** The standing document's bolt-ons generalise into one path that yields a count **and** its rows from a single walk, and both standing documents and unpushed work go through it. The module's central promise — one walk, so the badge, the `Needs you` group and the landing page cannot disagree — is what this protects; two more special cases would have been the third and fourth places for them to drift.

**Absent at zero is preserved, and therefore unknown is forbidden.** The badge is absent rather than zero, because a permanent `0` is the shape a reader learns to stop seeing. The cost of that rule is that *unknown* and *nothing owed* render identically — which is tolerable for a note (the corpus is always readable) and **not** tolerable for git, where [[ISS-0156]] means the open workspace currently has no count at all. So an obligation may only be admitted once its count is computable for every workspace, every time. **Unknown is a defect, not a state.**

## Alternatives

- **Keep the registry pure; run git through a parallel channel that renders identically.** Rejected. Two mechanisms producing the same badge in the same place is how they come to disagree, and this module exists precisely because a page and its own button disagreed. The purity being protected is also thinner than it looks: the registry already carries an obligation whose subject is not a note.
- **Leave unpushed work out.** Rejected. [[ADR-0022]] made the human the fallback publisher, and the surface built to say *"this needs you"* would then be silent about the one thing the human is uniquely responsible for.
- **Widen the definition.** Chosen. The badge's promise to a reader has always been the wider one — nobody reads `3` on the overview button as *three judgments about the record*.

## Consequences

- `obligations.py`'s docstring changes, and so does its test set: the completeness test that asserts every note type is declared gains a sibling asserting every **note-less source** is declared.
- Every obligation ships a noun and a verb, so a badge can say `3 · commits to push` rather than `3 items here need a person`.
- [[ADR-0020]] is unchanged and now applies to more: an obligation still surfaces in the view that owns its subject, and unpushed commits are owned by the overview, where history already draws them.
- [[ADR-0025]] is unchanged and now applies to more: the `Needs you` group is a shortcut list, so the git row appears there **and** in history, which is its structural place.
- The registry becomes the place to ask *"what else needs a person that we are not counting?"* — a question this decision makes answerable and does not answer. Nothing else is admitted here by implication.
