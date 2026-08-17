---
type: "[[decision]]"
id: ADR-0029
aliases: ["ADR-0029"]
title: "The acceptance mark vocabulary is Minimal's alternate checkboxes, and `[!]` reverses meaning"
status: accepted
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
decision_date: 2026-08-17
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
related: ["[[ADR-0028-Work-Has-Three-Phases]]", "[[FEAT-0104-The-Suite-Is-The-Surface]]", "[[ISS-0141]]", "[[ISS-0177-An-Exception-Mark-Drops-A-Check-With-No-Justification]]", "[[ISS-0185-The-Mark-Control-Sits-Inside-Tasklists-Leftover-Box-And-The-Cycle-Makes-You-Walk-Past-States]]"]
supersedes: []
tags: [acceptance, conventions]
---

# The acceptance mark vocabulary is Minimal's

## Context

An acceptance check has more than two outcomes, and this project has now picked a vocabulary for them **three times in two days**:

1. `[!]` as a release exception ([[FEAT-0104]]'s original plan). Minted here, written in **zero** suites fleet-wide, and shipped with no way to demand a justification ([[ISS-0177]]).
2. `[~]` and `[F]`, adopted because `../your-trainer`'s v2.1.0 suite already used them with a dated-verdict grammar. Measured: `x` 852, blank 151, `~` 7, `F` 1, `!` 0.
3. This one.

Edwin, 2026-08-17: *"can we use the commonly used checkbox values like they are defined here https://minimal.guide/checklists together with their styling."*

The argument for stopping the invention is that **there is a convention and it is not ours**. Minimal's alternate checkboxes are a documented set of 22 values used widely in Obsidian, which is the other tool that reads these files. A reader who knows `[-]` from anywhere else should not have to learn a local dialect, and a mark this project makes up has to be taught in a place nobody reads.

Neither `~` nor `F` is in Minimal's set. So adopting it is a fourth vocabulary — unless the old two are kept readable, which is what this decides.

## Decision

**The six marks the tool writes and reads are Minimal's**, with two legacy aliases read but never written.

| mark | Minimal calls it | here it means | gate | reason |
| --- | --- | --- | --- | --- |
| `[ ]` | to-do | nobody has walked it | **blocks** | — |
| `[x]` `[X]` | done | walked, passed | clears | optional witness |
| `[/]` `[~]` | incomplete | walked, **partial pass** | clears | **required** |
| `[-]` | canceled | **could not be run**, and not holding the release | clears | **required** |
| `[!]` `[F]` | important | walked, **failed**, tracked | **blocks** | **required** |
| `[?]` | question | the walker does not understand the check | **blocks** | **required** |

Four consequences follow, and each is a decision rather than a detail:

**1. `[!]` reverses meaning.** It was a release exception and did **not** block; it is now *failed* and **does** block. This is only safe because the mark is written in zero suites across twelve repos — verified before deciding, not after. Any `[!]` written between its introduction on 2026-08-16 and this decision would silently start blocking a release. None exists.

**2. The release exception moves from `[!]` to `[-]`.** The *concept* — a check that will not be done and is not holding the release — is unchanged and keeps its field (`Item.excepted`) and its separate count. Only its mark moves, to the value Minimal already gives that meaning.

**3. `[~]` aliases `[/]`, not `[-]`.** An earlier draft of this proposal had it aliasing `[-]`. Reading the seven live rows corrected it: every one says *"Partial pass"*, so `~` means incomplete, not canceled. The alias follows what the rows say rather than what would have been tidier.

**4. `[?]` and `[!]` both block, and so does `[ ]`.** Three blocking marks that mean three different things — nobody looked, somebody looked and it broke, somebody looked and could not tell. Collapsing any pair would lose the distinction the vocabulary exists for.

**Every mark but `[x]` and `[ ]` requires a reason to be written.** A check that clears the gate without being walked, or blocks it after being walked, is a claim about the release; the claim carries its evidence or it is refused ([[ISS-0177]]).

## Alternatives

**Keep `[~]`/`[F]`.** Already in the corpus, zero migration, no reversal. Rejected because it is a local dialect for something with a public convention, and because `F` has no natural partner for *partial* or *question* — the set does not extend.

**Invent a fuller set.** Rejected on its record: this would be the third invention, and the first one shipped a permissive mark with no accountability half.

**Adopt Minimal wholesale, all 22.** Rejected — `[S]` savings, `[f]` fire and `[w]` win have no meaning for a release gate, and offering them would be a menu of nonsense. Six are used; the other sixteen parse as unrecognised, which fails safe by blocking.

## Consequences

**Nothing in any repo needs editing.** `~` and `F` keep their meanings forever as aliases. The seven rows using them keep working.

**The styling is ours to write.** Minimal is an Obsidian theme; its CSS is Obsidian-specific. This adopts the *values and their names*, and implements a look of our own that follows them.

**`pymdownx.tasklist` renders none of the alternates**, which is already handled: the row draws its own control from `data-mark` ([[FEAT-0104]]), and that mechanism is mark-agnostic. Only the literal list it recognises has to widen.

**An unrecognised mark still blocks.** Sixteen Minimal values and every typo land there, which is the direction that fails safe and is unchanged since [[ISS-0141]].
