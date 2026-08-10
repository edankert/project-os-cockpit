---
type: "[[task]]"
id: TASK-0380
aliases: ["TASK-0380"]
title: "The standing set is declared as data — template-owned base, project extension in docs_system, one entry to exactly one file"
status: backlog
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
- [ ] One declaration of the standing set: path, what question it answers, whether it is required
- [ ] The base set is template-owned so every repo inherits the same answer to "what should exist"
- [ ] A project extends it through `SNAPSHOT.yaml`'s `docs_system` block, **without editing a template-owned file**
- [ ] Base and extension are merged by one function every consumer calls; no consumer reads only half
- [ ] An entry resolving to zero or two files is distinguishable from one resolving correctly
- [ ] Adding a document is a data edit — no code change anywhere

## Steps
- [ ] Put the base set with the other template-owned instruction data, so `sync-project-os.sh` carries it
- [ ] Extend `docs_system` in `SNAPSHOT.yaml` with a `standing:` list for project additions
- [ ] Write the merge + resolve function; return per-entry resolution rather than a boolean
- [ ] Test the sync case explicitly: a project addition survives `sync-project-os.sh`

## Notes
**The two layers exist because of the sync, not for elegance.** `sync-project-os.sh` copies `tools/instructions/`, `tools/skills/`, `docs/__templates__/` and `docs/__bases__/` wholesale — a project-specific entry living in any of those is silently destroyed on the next sync. `SNAPSHOT.yaml` is never synced, which is what makes it the right half for extensions.

**`docs_system` already exists and nothing reads it** — `source_of_truth`, `instructions`, `references`, no consumer anywhere in `src/` or `tools/`. This gives a dead field its first one, which is better than inventing a new block beside it.

**Singularity is the check that matters most.** "Only one appears in the repo" is the defining property of the class ([[REQ-0033]]); if an entry ever resolves to two files, the set has quietly become a type. Catch it by machine, early.
