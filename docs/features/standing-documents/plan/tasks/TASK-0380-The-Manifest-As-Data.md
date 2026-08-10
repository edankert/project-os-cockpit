---
type: "[[task]]"
id: TASK-0380
aliases: ["TASK-0380"]
title: "The standing set is declared as data — template-owned base, project extension in docs_system, one entry to exactly one file"
status: done
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-10
updated: 2026-08-10
source: ["[[REQ-0033-Every-Project-Can-Say-What-It-Is]]"]
parent: "[[FEAT-0091-The-Standing-Documents]]"
effort: M
due: ""
depends: []
blocks: ["[[TASK-0381-Statuses-Out-Checks-In]]", "[[TASK-0382-Standing-Documents-Land-On-Intent]]"]
related: []
tests: []
---

# The manifest as data

## Definition of Done
- [x] One declaration of the standing set: path, what question it answers, whether it is required
- [~] The base set is **in the app, not `tools/`** — see below; the property it was reaching for holds, the location does not
- [x] A project extends it through `SNAPSHOT.yaml`'s `docs_system` block, **without editing a template-owned file**
- [x] Base and extension are merged by one function every consumer calls; no consumer reads only half
- [x] An entry resolving to zero or two files is distinguishable from one resolving correctly
- [x] Adding a document is a data edit — no code change anywhere

## Steps
- [x] Put the base set with the other template-owned instruction data, so `sync-project-os.sh` carries it
- [x] Extend `docs_system` in `SNAPSHOT.yaml` with a `standing:` list for project additions
- [x] Write the merge + resolve function; return per-entry resolution rather than a boolean
- [x] Test the sync case explicitly: a project addition survives `sync-project-os.sh`

## Notes
**The two layers exist because of the sync, not for elegance.** `sync-project-os.sh` copies `tools/instructions/`, `tools/skills/`, `docs/__templates__/` and `docs/__bases__/` wholesale — a project-specific entry living in any of those is silently destroyed on the next sync. `SNAPSHOT.yaml` is never synced, which is what makes it the right half for extensions.

**`docs_system` already exists and nothing reads it** — `source_of_truth`, `instructions`, `references`, no consumer anywhere in `src/` or `tools/`. This gives a dead field its first one, which is better than inventing a new block beside it.

**Singularity is the check that matters most.** "Only one appears in the repo" is the defining property of the class ([[REQ-0033]]); if an entry ever resolves to two files, the set has quietly become a type. Catch it by machine, early.

## Done 2026-08-10 — with one criterion reconciled

`src/project_os_cockpit/standing.py`. `BASE_STANDING` is the eight documents [[ISS-0125]] measured; `manifest(project_root)` merges a project's `docs_system.standing` over it; `resolve()` reports each entry as **present · missing · ambiguous**.

### Why the base set is not template-owned

The DoD said *"template-owned so `sync-project-os.sh` carries it"*. That is worse than it sounds:

- `sync-project-os.sh` copies `tools/` **wholesale**, so anything a project added there is destroyed by the next sync — the exact hazard the two-layer split exists to avoid.
- The cockpit is **never installed into a downstream repo** (`CLAUDE.md`: *"Repos are consumed by discovery, not by a shim"*). There is nothing to sync it *into*.

One declaration in the app applies to every repo the cockpit renders, which is the property "template-owned" was reaching for. The extension half stays in `SNAPSHOT.yaml`, which is never synced and lives in the repo being described. **The split survives; only its upper half moved.**

### `docs_system` gets its first consumer

That block has existed with `source_of_truth`, `instructions` and `references` and **nothing has ever read it**. This gives it one rather than inventing a place beside it.

### The resolver's first cut said something about itself

`README` came back **ambiguous** — because a recursive `**/README.md` finds eight container-directory signposts, none of which is the project's README. That is a sentence about the search, not about the corpus. Resolution is now anchored to the docs root, with deeper copies reported as *rivals*; `README` is root-only, and the reason is written where the exclusion is.

`Resolution.paths` carries **every** match rather than the first, because a resolver that picked one would hide the drift REQ-0033 exists to catch — an entry with two files has quietly become a type.

### Verified against real corpora

`yourtrainer-mcp` reports `ARCHITECTURE`, `GLOSSARY`, `OWNERSHIP`, `DESIGN`, `STYLEGUIDE` **missing** — the five [[ISS-0125]] measured, and the case the presence check exists for.
