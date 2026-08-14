---
type: "[[task]]"
id: TASK-0421
aliases: ["TASK-0421"]
title: "An unknown count is unknown on every surface — the two renderer surfaces coerce a null `ahead` to zero and drop the row, which is the admission test the 2026-08-14 repair only fixed in Python"
status: done
owner: user:edwin
created: 2026-08-14
updated: 2026-08-14
phase: "[[PHASE-030-Obligations-Go-Home]]"
source: ["Reading [[ISS-0165]] on 2026-08-14 — the issue says the two implementations 'currently agree' and nothing is visibly wrong today; the renderer says otherwise"]
parent: "[[FEAT-0100-Unpushed-Work-Needs-A-Person]]"
effort: S
depends: []
blocks: []
related: ["[[ISS-0165-The-Attention-Card-Reads-A-Second-Git-Walk]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[TASK-0415]]"]
tests: []
---

# An unknown count is unknown on every surface

## What is wrong

[[ISS-0165]] says the two implementations of "how many commits are unpublished" *"currently agree"*, so the divergence is latent. **They do not agree today.** The 2026-08-14 repair — an unknown `ahead` may not render as nothing owed, [[ADR-0027]]'s fourth admission test — landed in `git_state.py` and `obligations._publication_rows`, which emits an explicit `publication-state-unknown` row. Neither renderer surface honours it:

- **The attention card** (`renderer.ts`, the `fleetHealth` loop that composes publication onto a card): `const ahead = typeof row.ahead === 'number' ? row.ahead : 0;` and then `if (ahead <= 0 && dirty <= 0) continue;`. An unknown becomes a zero and the row is dropped — *absent at zero*, precisely.
- **The fleet roll-up** (`buildHealthCard`): `behind` filters `typeof r.ahead === 'number' && r.ahead > 0`, and the separate "no remote" line keys on `remoteKind === 'none'`. A repo with a **backup remote and no upstream** is in neither list, so it renders as nothing at all.

So on 2026-08-14 the badge counts one publication obligation for such a repo while both other surfaces show nothing — the disagreement [[FEAT-0100]] claims cannot happen, live, in the shipped build. Independent review demonstrated the condition against a real repo the same day.

## What it must do

Say the worse fact, in the registry's own words: **no upstream is set, so nothing can say what is unpublished.**

- The attention card renders the publication line for an unknown count instead of dropping the card, and offers no push — there is no number to publish and no upstream to publish to. The row's action goes where the registry's row already points: History.
- The roll-up lists unknowns in their own line, beside "no remote" and never folded into a count or into silence.
- `publicationText` is the one place that turns a count into a sentence, so the unknown sentence lives there too rather than at each call site.

## Definition of Done

- [x] `ahead: number | null` survives from the payload to the sentence on both surfaces; nothing coerces null to 0.
- [x] A repo with a backup remote and no upstream appears on the attention card and in the roll-up, saying it cannot tell.
- [x] No push control is offered for an unknown count.
- [x] A node test builds that exact repo (real git, no upstream) and asserts both surfaces' inputs carry `null`, and a renderer-source guard asserts the coercion is gone.
- [x] The Python side is untouched — it already does this.
