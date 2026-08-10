---
type: "[[requirement]]"
id: REQ-0033
aliases: ["REQ-0033"]
title: "Every project can say what it is — the standing documents are declared as data, singular by construction, extensible without code, and their freshness is reported"
status: "draft"
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-10
updated: 2026-08-10
source: ["[[ISS-0125-The-Singleton-Documents-Have-No-Lifecycle-And-No-Home]]", "Edwin 2026-08-10: 'it would be good to make it possible/easy in the future to add to this set of documents of which only one appears in the repo'"]
priority: medium
scope: "The set of one-per-project standing documents, in this repo and in every project-os repo"
specifies: ["[[FEAT-0091-The-Standing-Documents]]"]
acceptance:
  - "The standing set is declared as data in one place; no renderer, validator or script carries its own list of document names"
  - "Adding a document to the set is a data edit — no code change, and no edit to a template-owned file for a project-specific addition"
  - "Every entry resolves to exactly one file; two files claiming one entry is an error, not a last-writer-wins"
  - "A missing required entry, a still-template entry, and a stale entry are each reported distinctly — staleness as a warning, never a build error"
  - "No entry carries a lifecycle status; freshness is carried by `updated:` and reported against it"
  - "The set is reachable from a surface a reader lands on, not only by knowing the path"
reviewed_by: ""
review_date: ""
review_verdict: ""
---

# Every project can say what it is

The documents that answer *what is this project* — its readme, index, architecture, glossary, ownership, design notes, style guide and phase registry — exist in 90 of 96 possible slots across the fleet and **94% of them are stale or undated** ([[ISS-0125]]). They are not missing. They are unnamed as a set, unchecked, and unreachable, and a document nobody is ever asked about is a document nobody updates.

## Why data rather than a type

A **type** is for an open population: there will be a ninth feature, a fortieth issue. There will never be a second glossary. This is a fixed set of named documents, so the thing that models it is a **manifest** — the shape `PHASES.md` already uses for phases.

But fixed is not frozen. Edwin, 2026-08-10: *"it would be good to make it possible/easy in the future to add to this set of documents of which only one appears in the repo."* So the manifest is data with two layers:

- **The base set is template-owned**, so every project-os repo inherits the same answer to "what should exist".
- **A project may extend it** in `SNAPSHOT.yaml`'s `docs_system` block — which exists today and **nothing reads**, so this gives a dead field its first consumer rather than inventing a place.

Extension must not require editing a template-owned file: `sync-project-os.sh` overwrites those, and a project addition living there would be silently destroyed by the next sync.

## Why singular is a check, not an assumption

"Only one appears in the repo" is the defining property of the class, so it is the property most worth asserting. An entry resolving to two files means the set has quietly become a type, and that is exactly the drift this requirement exists to catch — early, and by the machine, rather than by someone noticing a second glossary a year later.

## Why freshness warns and never blocks

A stale glossary is worth knowing about and worth nobody's build failing over. The pattern is the one upstream ADR-0011 established for independent review: warn, with a horizon, and escalate only if the warning proves ignorable. A blocking gate on documentation nobody is currently reading would be disabled within a week, which is worse than a warning that is occasionally skipped.
