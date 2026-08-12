---
type: "[[change]]"
id: CHG-20260812-Reasoning
title: "A judgment carries its reasoning — an optional note on any human verb, appended as an Obsidian callout, and a decision that states its open threads as criteria"
status: merged
date: 2026-08-12
owner: user:edwin
related: ["[[PHASE-032-The-Reasoning-Is-Recorded]]", "[[FEAT-0095]]", "[[FEAT-0096]]", "[[ISS-0152]]", "[[ADR-0010]]"]
tags: [change]
---

# The reasoning is recorded

[[ISS-0152]]'s options 3 and 1, both taken.

## What changed

**Any human transition may carry a note.** `TRANSITION_REQUEST_KEYS` gains `note`; it is appended to the note being decided under one `## Decision record` heading as a dated, attributed Obsidian callout — `> [!note] Accept — 2026-08-12 (user:edwin)`. It **appends** and never edits, and every line of the prose is quoted on the way in, so `---`, a heading or a nested callout cannot alter the file it lands in. Omitting it leaves the body byte-identical.

**The cockpit renders callouts.** It didn't: `> [!note]` came out as a plain blockquote with the literal marker still in it, which is what made this worth building before anything started writing them. Both front doors carry the rules — a decision record legible in the shell and not on the tablet is the divergence [[ADR-0010]] is about — and an unknown type keeps its title rather than printing `[!whatever]`.

**The actuator row has a field**, one for the row rather than one per verb, read at click time.

**A decision may state its open threads as criteria.** [[ADR-0010]] now carries its two — the deferred read-only digest, and `Recent`'s unresolved fate — as tickable criteria in its own words. Accepting with either open is allowed.

## Impact

- `POST /api/notes/transition` accepts `note` (≤2000 chars); everything else is unchanged.
- Notes gain a `## Decision record` section the first time a verb carries prose.
- `callouts.py` is new and registers on **every** render path, including notes rendered without a resolver.

## Documentation Coverage (All Types Considered)

- features: new ([[FEAT-0095]], [[FEAT-0096]]) · phase new ([[PHASE-032]])
- requirements: not-applicable
- tasks: new (five, all `done`)
- issues: resolved ([[ISS-0152]])
- tests: new (`tests/test_decision_reasoning.py`, 16 cases)
- workflows: not-applicable
- decisions: **upstream** — `project-os-dev` ADR-0020
- risks: not-applicable
- changes: new (this note)
- snapshot: updated

## Captured upstream, as asked

- **`project-os-dev` `d8b4742`** — ADR-0020 records the decision, its four rejected alternatives and why the callout is in the note rather than a log.
- **`project-os` `e4f3a44`** — `DECISIONS.md` carries both conventions with worked examples; `OBSIDIAN.md` makes callouts part of the record's vocabulary and states the unknown-type degradation so a downstream tool does not have to guess.

## Two of the four tasks needed no code

`criteria.py` already parsed an Acceptance section on any note and `stamp_tick` was never gated by type — so a decision's criteria were tickable before the convention existed. The owed mark on a structural row was the same story a day earlier. **The mechanism existed and had never been pointed at the case**, which is worth more than either fix: it is the second time in two days that reading the code first turned a feature into a convention.
