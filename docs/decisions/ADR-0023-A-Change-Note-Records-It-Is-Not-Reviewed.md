---
type: "[[adr]]"
id: ADR-0023
aliases: ["ADR-0023"]
title: "A change note records what happened; it does not owe a review — independent review keeps the three gates where a second pair of eyes changes an outcome"
status: "accepted"
owner: user:edwin
created: 2026-08-11
updated: 2026-08-11
source: ["Edwin 2026-08-11, using the app: 'Not sure why these CHG notes are open, they seem to in general store the changes that happened and do not need any review.'", "Measured 2026-08-11: the overview badge reads 87 and 87 of 87 are change-review obligations"]
decision: "A CHG-* note carries no independent-review obligation. Independent review is required for TST-* notes, requirement -> implemented, feature -> done, and release close-out."
related: ["[[ADR-0020-Obligations-Live-With-Their-Subject]]", "[[ISS-0123]]", "[[FEAT-0089-The-Obligation-Registry-And-The-Badges]]", "[[REL-0001-The-Human-Has-Levers]]"]
tags: [adr, quality, review]
---

# A change note records; it is not reviewed

## Context

**The overview's obligation badge reads 87, and all 87 are the same thing: *review this change note*.** Not most — every one. Measured 2026-08-11 from the registry's own breakdown, which is the surface [[FEAT-0089]] built precisely so a badge could say what it counts.

The obligation comes from `tools/instructions/QUALITY.md` line 48: *"Any change that creates or updates a `TST-*` or `CHG-*` note, and any transition to requirement `implemented` or feature `done`, requires an independent review pass."* The validator enforces it as a dated warning that **becomes an error on 2026-10-23**, citing `ADR-0011`.

### The rule's source cannot be read

`ADR-0011` could not be read from either repo a reader would look in. Not here, and not in the template: `~/Dev/repos/project-os/docs/decisions/` contains a single `README.md` and `counters.ADR` reads `0`.

> **Corrected 2026-08-12: it exists.** `ADR-0011-No-Permanent-Warning-Tier` is in `project-os-dev`, with sixteen siblings — the repo holding the design record for the system, which no citation names and which neither this repo nor the template contains. **The decision below was taken without it and stands**; ADR-0011 had itself left this very scope question open (*"it is either wired into close-out so it does run, or its scope narrows"*), so the two agree. What follows is kept as written, because what an unreachable citation costs is the point. [[ISS-0123]] carries the correction; [[ADR-0019]] is the upstream twin, and the template's `QUALITY.md` and `REVIEW_SETTLED_STATUSES` now carry it. Forty-one files here cite it, six upstream do, and the upstream six are all code, citing it *by clause*:

> `ADR-0011 clause 2: a warning is legal ONLY as a dated migration state.`
> `ADR-0011 clause 3 says a check is promoted to error only once the fleet carries…`
> `(ADR-0011 checks tests and changes for an independent-review stamp).`

So the rule is reconstructible only from the implementations that cite it. That is [[ISS-0123]]'s subject and this decision does not fix it — but it is the context in which "why do 87 notes owe a review?" turned out to have no readable answer.

## Decision

**A `CHG-*` note carries no independent-review obligation.**

Independent review is required for, and only for:

1. **`TST-*` notes** — the author of a fix must not be the sole judge of the test that guards it.
2. **requirement → `implemented`** and **feature → `done`** — a claim that something is finished.
3. **Release close-out** — the pass that produced nine findings on [[REL-0001]] and is the strongest evidence the gate is worth keeping.

## Why

**A change note is a record, not a claim.** It says *this happened*. The thing a reviewer could usefully challenge is the change itself — and the review that catches something happens at the gates above, against the diff and the notes, while the work is live. Reviewing the *note* six months later reviews the prose.

**The evidence is what the standing obligation actually produced.** 87 unreviewed CHG notes, the oldest from May, none of them reviewed by anyone in six months, all of them accruing toward an error date. An obligation nobody discharges is not a standard; it is a countdown, and the surface built to show what a person owes was spending its largest number on it.

**It was also crowding out the obligations that matter.** Five judgments across Intent, Issues and Features were sharing a badge row with 87 records-of-the-past. What is owed should be small enough to act on, which is the whole argument [[ADR-0020]] makes.

## Alternatives considered

- **Keep it, discharge in bulk at release time** — one pass per release covering every CHG since the last. Rejected: it keeps a gate whose value nobody can state, and turns it into a chore attached to the one moment already carrying the most work.
- **Keep it as-is and make the badge lead somewhere useful.** Rejected by Edwin: *"they seem to in general store the changes that happened and do not need any review"*. Making 87 six-month-old notes easier to work through is not the same as their being worth working through.
- **Write `ADR-0011` first, then decide.** Rejected as ordering: the decision is knowable without it, and reconstructing a phantom document in order to overrule part of it is work in the wrong direction. What is owed upstream is [[ISS-0123]]'s.

## Consequences

- `obligations.py` drops `change` from the owed kinds. The overview badge goes **87 → 0**; the registry total falls by 87 and its parts still sum to it, which `test_badge_total_equals_its_parts` already asserts.
- **The validator was not changed here on the day, and that was a limitation rather than an oversight.** `tools/scripts/` is template-owned, so a local edit would have been reverted by the next sync. **Landed upstream on 2026-08-12** instead: [[ADR-0019]] in `project-os-dev`, and `QUALITY.md` + `REVIEW_SETTLED_STATUSES` in the template, from where this repo took it. The 87 `[REVIEW]` warnings are 0 and the 2026-10-23 promotion now lands on tests alone. The disagreement between the surface and the validator lasted one day and is recorded rather than tidied away.
- What changes today is what this repo owns: the registry. `change` leaves the owed kinds, so the surface stops asking for something the decision says is not owed, while the validator keeps saying it until upstream catches up. The two disagreeing is uncomfortable and is the honest state — recorded rather than hidden by editing a file that would be overwritten.
- `QUALITY.md` is **template-owned**, so this repo's copy is not the place to edit the sentence. The rule lives here until it is proposed and accepted upstream — the same shape as the close-out-commit and file-what-you-cannot-fix rules already recorded in `CLAUDE.md`.
- Reviewing a change note remains *possible* and is never wrong; it stops being *owed*.

## Who decided

**Edwin, 2026-08-11**, choosing between three stated options after the measurement above was put in front of him. Recorded `accepted` rather than `proposed` because the human made the call in session — the same reason [[DES-0009]] could only be accepted by him and not by the session that wrote it.
