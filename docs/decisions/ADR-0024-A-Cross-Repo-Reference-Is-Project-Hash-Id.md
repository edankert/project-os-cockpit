---
type: "[[adr]]"
id: ADR-0024
aliases: ["ADR-0024"]
title: "A reference to another project's note is `[[project-id#NOTE-ID]]` — the separator is `#` because what follows it is an id, not a path"
status: "accepted"
owner: user:edwin
created: 2026-08-12
updated: 2026-08-12
source: ["Edwin 2026-08-12: 'do we need a way to reference notes in other projects by maybe prefixing the ID?'", "Edwin 2026-08-12: 'instead of the / can we use the # notation'"]
decision: "Cross-repo references take the form `[[<project-id>#<NOTE-ID>]]`, where project-id is `project.id` from that repo's SNAPSHOT.yaml, defaulting to its directory name. A bare `[[NOTE-ID]]` keeps its current meaning: this repo, or broken."
related: ["[[ISS-0148]]", "[[ISS-0123]]", "[[FEAT-0093]]", "[[project-os-dev#ADR-0019]]"]
tags: [adr, traceability, fleet]
---

# A cross-repo reference is `project#ID`

## Context

The fleet references itself constantly and has never had a way to say so. **41 files in this repo and 6 in the template cite `ADR-0011` or `ADR-0013`** — notes that exist, in `project-os-dev`, which no citation names. Every one renders as a broken wikilink, and the cost was measured on 2026-08-12: a session prepared to write a replacement for a decision that had been sitting upstream for a year, and only avoided it by checking a third repo on a hunch ([[ISS-0123]]).

## Decision

**`[[<project-id>#<NOTE-ID>]]`** — for example `[[project-os-dev#ADR-0011]]`.

- **`project-id`** is `project.id` from that repo's `SNAPSHOT.yaml`, defaulting to its **directory name**.
- **A bare `[[NOTE-ID]]` is unchanged**: this repo, or broken. No existing link acquires a new meaning.

## Why `#` and not `/`

**`/` was recommended on 2026-08-11 and the argument for it was wrong.** It rested on the slash form resolving natively in Obsidian if the vault were ever opened at `~/Dev/repos`. It would not: project-os links are **id-shaped and resolve through `aliases:`**, not through paths, and `project-os-dev/ADR-0011` is not a path either — the file is `project-os-dev/docs/decisions/ADR-0011-No-Permanent-Warning-Tier.md`. Both forms are equally unresolved in Obsidian. The claim was made without checking and is withdrawn.

With that gone, `#` wins on what the parts actually are:

- **What follows the separator is an id, not a path segment.** `/` promises a directory structure that does not exist and invites a reader to go looking for `project-os-dev/ADR-0011` on disk. `#` reads as *"this id, within that project"* — a fragment, which is what it is.
- **`#` already means "a location inside a thing"** everywhere else a reader has met it: URL fragments, and Obsidian's own heading anchors.
- **The Obsidian collision is harmless.** There, `[[project-os-dev#ADR-0011]]` parses as *"heading ADR-0011 in a note called project-os-dev"*, finds no such note, and renders unresolved — which is precisely what those citations do today. It fails to resolve; it does not resolve to the wrong thing, which is the property that matters.

## Why the id is the directory name and not `project.name`

Measured 2026-08-12: `project.name` carries spaces and capitals (`Obsidian-Supernote Sync`, `Your Health`) and the template's still reads **`REPLACE ME`**. It is a display string. The shell's workspace id is `sha1(path)` — machine-local, so it cannot be written into a committed note. The directory name is clean, unique across all twelve repos, and is what a person types when they mean that project.

`project.id` exists as an override for the case the default cannot survive: a repo renamed or cloned into a different folder changes identity silently, and every reference to it breaks with no error anywhere.

## Consequences

- [[FEAT-0093]] implements parsing, rendering and following. The sidecar cannot resolve another repo and must not pretend to: it emits the two parts as data and the shell — which knows the fleet — does the lookup.
- **A reference to a project not on this machine must say so.** An unresolvable cross-repo link that looked identical to a resolvable one would reintroduce the silence this fixes.
- The 47 existing citations are **not** swept here. The notation has to exist before anything can be rewritten, and the churn is a separate decision ([[ISS-0148]]).
- This is a fleet convention and therefore template-owned: `OBSIDIAN.md` and `TRACEABILITY.md` should carry it, which makes it an upstream decision in `project-os-dev` as well. Recorded here first because the implementation is here.
