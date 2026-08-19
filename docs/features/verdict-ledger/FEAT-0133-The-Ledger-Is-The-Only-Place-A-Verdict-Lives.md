---
type: "[[feature]]"
id: FEAT-0133
aliases: ["FEAT-0133"]
title: "The ledger is a file — append-only, one per release per platform — and it is the only place a verdict lives"
status: backlog
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
goal: "An acceptance verdict is a dated, attributed event in a single-platform, per-release ledger, so the stored fact has the same arity as the real one."
requirements: ["[[REQ-0052-A-Verdict-Names-Its-Platform-Method-Author-And-Date]]"]
tasks: ["[[TASK-0527-The-Ledger-Schema-And-The-Working-Ledger]]", "[[TASK-0528-The-Validator-Reads-A-Ledger]]", "[[TASK-0529-Backfill-One-Ledger-Per-Repo]]"]
related: ["[[ADR-0037-A-Verdict-Is-An-Event]]", "[[ADR-0020-Obligations-Live-With-Their-Subject]]", "[[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]]", "[[ISS-0206-A-Check-Cannot-Belong-To-A-Release]]"]
tags: [feature]
---

# The ledger

## Goal

A verdict is a fact about **(check × platform × release)**. Give it a container with three dimensions.

`docs/releases/ledgers/REL-####-<platform>.yaml`, plus one open `WORKING-<platform>.yaml` per platform. Append-only. Plain YAML, hand-editable, one entry per list item. Sealed at release cut and never edited afterwards.

## Scope

- The file schema: `release`, `version`, `platform`, `sealed`, `entries[]`.
- The entry schema: `check`, `mark`, `date`, `by`, `method`, and `reason` where the mark demands one; or `invalidated_by` + `date` for an invalidation event.
- **The working ledger.** There is always exactly one open ledger per platform, and every event lands in it. **Sealing is what assigns an event to a release** — which is [[ISS-0206]]'s third open question answered without a field on anything.
- Sealing: the working ledger gains `release:`, `version:` and `sealed:`, is renamed, and a fresh working ledger starts.
- Immutability of a sealed ledger, enforced by the validator.
- The backfill: one ledger per repo from today's scalar marks.

## Out of scope

- Reading it. [[FEAT-0135]] owns the queries; [[FEAT-0136]] owns the cockpit.
- Removing anything from a note. [[FEAT-0134]].

## The honest part of the backfill

**All 546 `pass` verdicts in the fleet have no date** — `verdict_date:` is empty on 671 of 671 notes. The backfill writes the migration date with `by: migration` and a `note:` saying the verdict predates the ledger, naming the pre-migration address from `migrated_from:`. Recovering true dates from `git log -L` is possible and is deliberately **not** done: partial precision that looks total is worse than an honest stamp.

And the platform is the point: `your-trainer`'s 513 passes were earned on Android and go into an Android ledger. From that moment they stop counting toward an iOS release, which is the whole honesty gain and a large gate movement — [[TASK-0529]] measures it before it lands.

## Acceptance

- [ ] A ledger file exists with a documented schema, and a working ledger per platform.
- [ ] An entry without a platform (from its file), a method, an author or a date is refused.
- [ ] `fail`, `partial`, `blocked`, `question` and `na` are refused without a reason; `pass` is not.
- [ ] A sealed ledger cannot be modified — proved by a test that tries.
- [ ] One release is backfilled per repo, with the gate delta measured and stated first.
