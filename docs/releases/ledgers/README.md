# Acceptance ledgers

**A verdict is an event, not a field** ([[ADR-0037-A-Verdict-Is-An-Event]]).

An acceptance verdict is a fact about **(check × platform × release)**. It used to be a scalar `mark:` in the check note's frontmatter, and a scalar cannot hold a three-tuple — measured before deciding: 579 of `your-trainer`'s 581 acceptance notes carried no platform at all, while every one of its 513 passes had been earned on Android.

These files are the container with the right arity.

## What is in here

| file | what it is |
| --- | --- |
| `WORKING-<platform>.json` | **the open ledger.** Exactly one per platform. Every event lands here |
| `REL-####-<platform>.json` | **a sealed ledger.** Immutable. What that release was actually verified against |

There is no cross-platform ledger, and that is by construction rather than by omission: releases are per-platform in any repo shipping independent cadences (`your-trainer` ships `v2.1.6` and `ios/v0.1.0` from separate tag namespaces), so there is no cross-platform release object to hang a shared one on. **The cross-platform view is a query across ledgers, not a document** — `ledger.burndown()`.

## The lifecycle

1. A walk, a runner or a migration **appends** an event to `WORKING-<platform>.json`.
2. At release cut the working ledger is **sealed**: it gains `release`, `version` and `sealed`, is renamed to `REL-####-<platform>.json`, and a fresh working ledger starts.
3. A sealed ledger is **never edited**. `LEDGER-SEALED` in the validator enforces it against `HEAD`.

**Sealing does two things and only one is bookkeeping.** It assigns every event in the file to a release — which is how a check belongs to a release without any field saying so — and it is **when `excused` expires**.

## The outcomes

| mark | gate | survives the seal |
| --- | --- | --- |
| `pass` | clears | yes, until invalidated |
| `partial` | clears | yes, until invalidated |
| `na` — cannot apply here | clears | yes, until invalidated |
| `excused` — not done this cycle, by decision | clears | **no** |
| `blocked` — could not be run right now | **blocks** | no |
| `fail` | **blocks** | no |
| `question` — the *check* is not understood | **blocks** | no |
| *(no entry)* | **blocks** | — |

Every mark but `pass` is refused without a `reason`.

**"Not run" is three answers and only two of them clear.** `na` and `excused` are decisions somebody made about this release. `blocked` is an accident that will be gone next week, and a gate that clears because the rig was down clears on whatever happens to be broken that day.

**`na` and `excused` differ in exactly one property: whether the exception comes back.** `na` is about the check and the platform, so re-asking it every release would be the maintained-matrix failure this whole design removes. `excused` is about the check, the platform **and this release** — and if it persisted, a check excused once would be excused forever.

That is not hypothetical. It is what the code did before these files existed: `Item.excepted` was read from frontmatter and scoped to nothing, while the comment above it still described the per-release property [[ADR-0029]] designed and lost when it moved the release exception from `[!]` to `[-]`. **A field on a note cannot hold *"expires with its release"* at any price.** An event in a per-release ledger gets it by construction, because the ledger it sits in *is* the release it applies to.

## There is no "not yet walked"

You do not record that you did not do something. **No entry for a platform means owed on that platform** — so adding a platform makes every check immediately owed there, with no schema change, no key to add and no backfill. The absence *is* the initial state, and it is the honest one.

## Editing these by hand

You can, and the format is meant to survive it: one entry per line, so a diff reads as *what was added*. But you rarely should — `ledger.append()` validates before writing, and the validator will refuse anything malformed at pre-commit either way.

**JSON rather than YAML** (Edwin, 2026-08-19): this project has never written YAML — `yaml.dump` occurs zero times in `src/` and `tools/scripts/` — so a YAML ledger would mean its first hand-rolled YAML writer, on the file a CI runner appends to most often. And YAML's implicit typing (`no` → `False`, a bare date → `date`) is a live hazard on a file of ids, dates and short words.

## What this does not see

**A behaviour with no check.** The ledger makes coverage *legible*, not complete. A surface nobody wrote a check for is still invisible here, and that gap closes through [[FEAT-0130]] and [[FEAT-0132]] — not through these files. Do not read a clean ledger as a verified release; read it as *everything anybody thought to ask about is answered*.
