---
type: instruction
id: INSTR-TAXONOMY
status: active
owner: group:maintainers
created: 2026-01-27
updated: 2026-07-17
tags: [instructions, taxonomy]
---

# Taxonomy (allowed values)

This file defines default allowed values for common fields so multiple agents/LLMs stay consistent.

Projects may override; if you do, update templates and any automation that assumes these values.

## `owner` (all notes)
See `OWNERSHIP.md` for allowed formats and the canonical registry.

## `severity` (issues)
- `low`, `medium`, `high`, `critical`

## `priority` (requirements)
- `low`, `medium`, `high`

## `order` (phases)
Positive integer sort order for roadmap sequencing.

## `effort` (tasks)
- `XS`, `S`, `M`, `L`, `XL`

## `likelihood` (risks)
- `low`, `medium`, `high`

## `impact` (risks)
- `low`, `medium`, `high`

## `component` (issues)
Project-defined free text label, but keep it stable. Examples:
- `docs`, `build`, `tests`, `tooling`, `runtime`, `ui`, `api`

## `kind` (tests)
- `manual`, `automated`

## `level` (tests)
- `unit`, `integration`, `system`, `e2e`, `acceptance`
- **`acceptance` is the discriminator of the merged type (ADR-0031)**: a test at this level is the thing a person walks — it rests at `status: active`, its verdict is `mark:`, and it carries the acceptance fields below. Everything else on the scale is executable. The field has always been here; since ADR-0031 it carries the distinction the retired `check` type used to.
- A test moves along the scale rather than between types. **Adding a `command:` to an `acceptance` test is how a walk becomes automated**, and a `passing` test named in another's `covered_by:` settles it (see `TESTING.md` tiers and `../skills/release-verification/SKILL.md`).

## `acceptance:` on a feature (FEAT-0064)

Distinct from the test kind above, and easy to confuse with it: this is a **frontmatter field on a `[[feature]]`**, recording whether a human has accepted the work against its requirements' criteria.

| value | meaning |
|---|---|
| absent / `""` | **no gate** — the default, and it stays the default |
| `requested` | the feature opted in; a human owes it an acceptance run. Stamped at **close-out** by the agent |
| `accepted` | a completed run stamped it, together with `accepted_by` and `accepted_date` |

**Opt-in, never mandatory.** A gate on the one judgment that cannot be automated becomes a rubber stamp — `PHASE-024`'s framing, and the reason `requested` never blocks an agent's close-out. It keeps the debt visible until a run discharges it.

**The agent asks; it never answers.** An agent may stamp `requested`. Only a completed acceptance run writes `accepted`/`accepted_by`, and that run is loopback-only and human-initiated (`REQ-0026`, `REQ-0028`).

*Locally added ahead of upstream — see the local divergence note in `SYNCING.md` and the upstream proposal that carries it home.*

## `design:` on a feature (FEAT-0070)

Optional. Names the `[[design]]` a feature is built against — *design before code*, made mechanical to the extent it can be.

`DESIGN-GATE` **warns** when a feature has left the pending band (`backlog`, `planned`, `deferred`, `cancelled`, `superseded`) while the design it names was **never accepted**. `accepted`, `implemented` and `superseded` all satisfy it: `accepted → implemented` is the normal progression and `superseded` means a later design replaced one that had been accepted.

That set was narrowed after the first cut fired **five false positives on this corpus immediately** — every one a design that had progressed past `accepted`. A nag that fires wrongly is the fastest way to teach somebody to ignore it, which is also why this warns rather than blocks: the judgment being gated (*is this design right?*) cannot be automated, and a blocking gate on it gets cleared to unblock the build.

*Locally added ahead of upstream, like `acceptance:` above.*

## `scope` (tests)
- `feature`, `system`

## Acceptance outcomes (the ledger's vocabulary)

The verdict on an acceptance test is **an event in a per-release, single-platform ledger**, not a field on the note (ADR-0037). It is a fact about *(check × platform × release)* and a scalar cannot hold a three-tuple — measured before deciding: 579 of `your-trainer`'s 581 acceptance notes carried no platform at all, while every one of its 513 passes was earned on Android.

| mark | means | gate | survives the seal |
|---|---|---|---|
| `pass` | walked, and it held | clears | yes, until invalidated |
| `partial` | some clauses hold, some do not | clears | yes, until invalidated |
| `na` | **cannot apply here** — no such surface on this platform | clears | yes, until invalidated |
| `excused` | **not done this cycle, by decision** — out of scope, low risk, no time | clears | **no — expires with its release** |
| `blocked` | **could not be run right now** — rig down, device unavailable | **blocks** | no |
| `question` | walked, and the *check* is not understood | **blocks** | no |
| `fail` | walked, and it failed | **blocks** | no |
| *(no entry)* | nobody has run it on this platform | **blocks** | — |

**Every mark but `pass` is refused without a reason.** A check that clears the gate without being run, or blocks it after being run, is a claim about the release; the claim carries its evidence or it is refused.

**"Not run" is three answers, not one, and only two of them clear.** `na` and `excused` are *decisions* somebody made about this release; `blocked` is an *accident* that will be gone next week, and a gate that clears because the rig was down clears on whatever happens to be broken that day.

**`na` and `excused` differ in exactly one property and it is the one that matters: whether the exception comes back.** `na` is about the check and the platform, so re-asking it every release is the maintained-matrix failure this design removes. `excused` is about the check, the platform **and this release** — and a field on a note cannot hold *"expires with its release"* at any price, which is how ADR-0029's per-release exception silently became permanent when its mark moved from `[!]` to `[-]`.

**There is no "not yet walked" value.** You do not record that you did not do something: no entry for a platform means owed on that platform, so adding a platform makes every check immediately owed there with no schema change and no backfill.

**An invalidation is an event, not a mark.** `{check, invalidated_by, date}` sitting after the verdict it overtakes — which is why `rerun` is not in this table.

### Legacy values, read forever and never written

Two earlier vocabularies stay **readable** so that a repo mid-migration keeps working; neither is current, and nothing writes them.

| era | values |
|---|---|
| ADR-0029 — [Minimal's alternate checkboxes](https://minimal.guide/checklists) | `" "` `x` `/` `-` `!` `?` |
| ADR-0034 — the same distinctions as words | `todo` `done` `incomplete` `canceled` `important` `question` `rerun` |

The mapping into the ledger is `done`→`pass`, `incomplete`→`partial`, **`canceled`→`na` (never `excused`)**, `important`→`fail`, `question`→`question`, `todo`→*no entry*, `rerun`→*an invalidation*.

`canceled` gets a written rule because one old value has two successors: a migration that guessed would either make a permanent exception expire or make a per-release one permanent. `na` is right for a backfill — nothing in the old field said which release it belonged to, and `excused` is precisely the value that claims one.

**`mark:` is not `status:`.** An acceptance test's lifecycle is `status:` — it rests at `active`, and `retired` is terminal. Its verdict is not on the note at all. That is what keeps it outside the runner-only rule, the independent-review gate and the `Run` obligation — see `STATUSES.md` `[[test]]`.

## `burden` (tests at `level: acceptance`)
Optional, project-defined free text naming what a walker must have to hand — `App`, `Trainer`, `Strava`, `hardware`. Its purpose is to avoid making somebody set the same thing up twice, so keep the labels stable and few.

## `check` — retired (ADR-0031)

**There is no `check` type.** An acceptance check is a `[[test]]` at `level: acceptance`; a note that carried `type: "[[check]]"` was migrated, keeping its old id as an alias.

*(This heading read "`check` versus `level: acceptance` on a test — Both exist and they are not the same thing…" until 2026-08-19. It survived ADR-0031 by nobody reading past the mark table, and was then copied into two more repos by the very sync that was fixing [[ISS-0217]] — the drift travelling under its own fix. The ISS-0218 drift check reads the mark TABLE and cannot see prose, which is why this one needed a person.)*
