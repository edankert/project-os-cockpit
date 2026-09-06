---
type: "[[change]]"
id: CHG-20260906-Deck-Collateral-Moved
title: "The new-application design collateral moved to project-os-deck; the cockpit stays the primary place for new functionality and keeps a capability register the sibling tracks"
status: merged
owner: user:edwin
created: 2026-09-06
updated: 2026-09-06
source: ["Edwin 2026-09-06: 'Can we create a new repo for this ... move all the design collateral from here into the new repo (not to confuse this repo) and make sure to mark the current cockpit functionality so if any new cockpit functionality arrives which it will that we can adapt the other repo accordingly.'"]
commit: ""
pr: ""
impacts: []
issues: ["[[ISS-0279]]"]
features: []
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[REFERENCE-CAPABILITY-REGISTER]]", "[[PHASE-028-Borrowed-Capability]]", "[[project-os-deck#REFERENCE-SURFACE-ARCHITECTURE-OPTIONS]]", "[[project-os-deck#DES-0002]]"]
---

# The new-application design collateral moved to project-os-deck

## Summary

Nine notes and two HTML prototypes that designed the next application left this repository on 2026-09-06 for a new one, `~/Dev/repos/project-os-deck`, and anyone following a link to DES-0013, DES-0014 or FEAT-0144 from here now lands in that repository. The cockpit itself is unchanged in behaviour. What it gained is a register: the capability register here is the contract Deck tracks, and this cockpit remains the primary place where new functionality is built. An earlier wording of this note, the same day, said the cockpit was frozen except for fixes and that new capability would land in Deck; Edwin reversed that within the hour ("too early to say that any new cockpit functionality should land in the deck instead"), so Deck's obligation is to keep an eye on what arrives here and be able to support it.

## What moved, and to what

| here, before | in project-os-deck, now |
| --- | --- |
| DES-0013 Nine Ways To Read The Record, with its HTML | DES-0001 |
| DES-0014 The Glass Cockpit, with its HTML | DES-0002 |
| FEAT-0144 The Corpus Has An Inside, with its plan | FEAT-0001 |
| TASK-0592 to TASK-0596 | TASK-0001 to TASK-0005 |
| docs/reference/des-0014-glass-cockpit-review-2026-09-05.md | docs/reference/des-0002-glass-cockpit-review-2026-09-05.md |
| docs/reference/cockpit-surface-architecture-options-2026-09-06.md | same path |

The counters here were not reused: DES stays at 14, FEAT at 144, TASK at 596. Each moved note carries a Provenance section naming its old id and the last commit here (`74172d8`). Links from the moved notes to notes that stayed use the `[[project-os-cockpit#ID]]` form; links from here to the moved notes use `[[project-os-deck#ID]]`.

## What stayed, on purpose

- `docs/reference/cockpit-capability-register.md`: every shell capability, sidecar API group and surface under a stable key at baseline `570da22`, with the rule that a change note adding, changing or retiring capability updates it in the same commit.
- ISS-0279 (a list-valued `type:` is dropped by the indexer): a sidecar bug, so it stays with the sidecar; Deck's Vault phase will pick it up.
- DES-0001 to DES-0012: they document this cockpit as built, and DES-0002 is the token source the code compares against.

## Impact

- `SNAPSHOT.yaml`: the eight moved items left `items:`; the focus note records the move; counters unchanged.
- `PHASE-028`, `ISS-0213`, `ISS-0278`, `ISS-0279` and the register: links repointed to `project-os-deck#`.
- `CLAUDE.md`: the sibling section names the repository and the adoption table.
- The shell's workspace discovery finds the new repository on the next rescan, because it carries a `SNAPSHOT.yaml` under `~/Dev/repos/`.

## Documentation Coverage (All Types Considered)

- features: updated (FEAT-0144 removed from the snapshot; lives in project-os-deck)
- requirements: not-applicable
- tasks: updated (TASK-0592 to 0596 removed from the snapshot)
- issues: updated (ISS-0279 repointed; stays here)
- tests: not-applicable
- workflows: not-applicable
- decisions: not-applicable (a "Canopy beside Cockpit" ADR is Deck's to write, per the options note Part 8)
- risks: not-applicable
- changes: new (this note)
- snapshot: updated

## Follow-ups

- [ ] Deck writes its "beside the cockpit" ADR and opens its first phase.
- [ ] The register's detection command is run at Deck's grooming and the adoption table dated.
