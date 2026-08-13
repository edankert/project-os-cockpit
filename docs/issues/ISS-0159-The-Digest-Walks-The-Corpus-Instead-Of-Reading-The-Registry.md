---
type: "[[issue]]"
id: ISS-0159
aliases: ["ISS-0159"]
title: "The digest counts what needs you with its own walk, so it cannot see an obligation whose subject is not a note — measured 13 against the registry's 14"
status: "fixed"
owner: user:edwin
created: 2026-08-13
updated: "2026-08-13"
source: ["Found while building [[TASK-0418]], 2026-08-13; named in [[PHASE-030]]'s close-out as work it was leaving behind"]
severity: medium
component: docs-system
parent: ""
related: ["[[FEAT-0089-The-Obligation-Registry-And-The-Badges]]", "[[FEAT-0071]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[TASK-0416-Generalise-The-Note-Less-Obligation]]", "[[PHASE-030-Obligations-Go-Home]]"]
tests: []
---

# The digest walks the corpus instead of reading the registry

## Problem

`digest_payload` builds its `needs_you` list by walking `index.paths()` itself and asking `_owed_flag` per record. The **predicate** is the registry's — `_owed_flag` calls `obligations.for_type` and `_is_owed`, and says so — but the **walk** is its own.

That walk can only see notes. Every obligation whose subject is *not* a note is therefore invisible to it: standing documents, unpushed commits, undeployed commits. [[ADR-0027]] made those first-class and [[TASK-0416]] gave them a declared path that `owed_items()` already returns; the digest predates both and still does its own pass.

## Measured, 2026-08-13

```
digest needs_you_count : 13
registry total         : 14   {features 4, tests 1, overview 1, intent 1, issues 7}
note-less rows         : {overview: 1}
difference             : 1
```

The difference **is** the note-less count. It is one today only because this repo's standing set is current and it has just been pushed; on a repo with eight stale standing documents and thirty unpushed commits the two numbers are thirty-eight apart, describing the same project on the same screen — the attention card's *"N need you"* against the view badges' total.

## Why it matters beyond the number

This is the failure [[PHASE-030]] existed to end, surviving inside the phase that ended it. The registry's whole promise is *one walk, so the badge and the page cannot disagree* — `counts_by_kind` is asserted against `owed_items` for exactly this reason. A third walk is outside that assertion and so cannot be caught by it.

## Not a simple substitution

The digest is **not** just the registry: it also adds notes carrying an owed `review_verdict` ([[ISS-0121]]'s discriminator — a sticky `changes-requested` on a note that has since reached a terminal status is *not* owed). The registry does not count those.

So the fix is not "call `owed_items` instead". It is:

1. take the registry's rows from `owed_items()` — one walk, note-backed **and** note-less;
2. keep the verdict set as a **declared, named** addition rather than an accident of a separate pass;
3. make the relationship assertable: the digest is the registry's total plus a set it can enumerate, never silently less.

## Expected

`needs_you_count` never under-reports what the badges show for the same project.

## Actual

It under-reports by exactly the note-less obligations, silently, and the two numbers sit on adjacent surfaces.

## Fixed — 2026-08-13

`digest_payload` now takes its owed rows from `obligations.owed_items(index)` — the registry's own walk, note-backed and note-less together — and the verdict set is appended as a **declared** addition rather than arriving from a second pass nobody named.

Measured before and after on this repo: **13 → 14**, against a registry total of 14.

`test_the_digest_never_under_reports_what_the_badges_show` asserts `digest >= registry` and that every owed id is present by id rather than merely covered by the total. Mutation-checked: dropping the note-less rows again fails it.

## One documented invariant changed, and it should be said plainly

`test_the_digest_and_the_badges_count_the_same_things` asserted `badges - standing`, calling the standing gap **deliberate**: *"their subject is a manifest entry rather than a note, and the digest is a note digest."* That test now asserts `digest >= badges`, so this fix overturned a written decision rather than merely repairing an oversight.

Two things that were true when it was written had stopped being true:

- **`owed_items` had no rows for a note-less obligation**, so the digest could not have included one had it wanted to. [[TASK-0416]] gave them rows the same week.
- **The `needs_you` *list* is no longer rendered anywhere.** [[ISS-0145]] took it off the band — *"an obligation is not news"* — leaving only the **count**, on the attention card, beside the very badges it disagreed with. A note-shaped list was a defensible thing to scope to notes; a count of what needs a person is not.

So the gap was a limitation described as a principle. [[TASK-0313]]'s own stated intent is what now holds: *"it reads from FEAT-0089's registry once that lands."*
