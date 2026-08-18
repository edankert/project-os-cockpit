---
type: "[[feature]]"
id: FEAT-0093
aliases: ["FEAT-0093"]
title: "A note in another project is one click away — `[[project#ID]]` resolves across the fleet, and the cockpit switches workspace and opens it"
status: done
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-12
updated: 2026-08-12
source: ["Edwin 2026-08-12: 'do we need a way to reference notes in other projects by maybe prefixing the ID?'", "Edwin 2026-08-12: 'instead of the / can we use the # notation and where how is this project id defined, also we need in the cockpit to be able to jump to this location if this notation is used in text'", "Measured: 41 files here and 6 in the template cite ADR-0011/ADR-0013, every one a broken wikilink"]
goal: "`[[project-os-dev#ADR-0011]]` renders as a link wherever a wikilink renders, and clicking it switches to that workspace and opens that note."
requirements: []
tasks:
  - "[[TASK-0390-The-Project-Id]]"
  - "[[TASK-0391-The-Cross-Repo-Wikilink]]"
  - "[[TASK-0392-Following-It]]"
related: ["[[ISS-0148]]", "[[ISS-0123]]", "[[FEAT-0016]]", "[[ADR-0024]]"]

---

# A note in another project is one click away

## Goal

The fleet references itself constantly and has no way to say so. **41 files here and 6 in the template cite `ADR-0011` or `ADR-0013`** — notes that exist, in `project-os-dev`, which no citation names. Every one of those renders as `<span class="broken-wikilink">`, which is the cockpit correctly reporting that it cannot find something it was never told where to look for.

The cockpit is the only tool that can fix this. It discovers every `SNAPSHOT.yaml`-bearing repo and runs a sidecar per workspace ([[FEAT-0016]]), so it already holds the map a cross-repo link needs. A text editor cannot.

## Out of scope

- **Sweeping the 47 existing citations.** The notation has to exist before anything can be rewritten to use it, and the sweep is a separate decision about churn ([[ISS-0148]]).
- **Cross-repo *writes*.** Following a link is reading. Ticking a criterion in another repo from here is a different feature and a much bigger one — every write guard is per-sidecar and loopback-bound ([[REQ-0027]]).
- **Obsidian resolution.** `#` is heading syntax there, so these stay unresolved in Obsidian exactly as they are today. That is the accepted cost ([[ADR-0024]]).

## Acceptance

- [x] Every workspace has a stable, writable **project id** — `project.id` in `SNAPSHOT.yaml`, defaulting to the repo's directory name, exposed on the workspace and in the sidecar's own payloads.
- [x] `[[project-os-dev#ADR-0011]]` renders as a **link**, not as broken-wikilink text, in the note body and in the frontmatter strip — both of the two consumers `wikilinks.py` names.
- [x] The link carries the two parts as data rather than a guessed URL: the sidecar cannot resolve another repo and must not pretend to.
- [x] Clicking it **switches workspace and opens the note**, and back returns to where you were.
- [x] A reference to a project that is not on this machine says so and does not navigate — an unresolvable cross-repo link must not look identical to a resolvable one.
- [x] `[[ADR-0011]]` with no prefix keeps its current meaning exactly: this repo, or broken. No existing link changes behaviour.

## Evidence — 2026-08-12

`project_id()` returns the directory name for all twelve repos and the explicit field when set. [[ISS-0123]] now carries **the first two real cross-repo links in the fleet**, and the sidecar renders them as `class="cross-repo-link" data-project="project-os-dev" data-note-id="ADR-0011"` — data, not a URL. Both ends of the lookup answered: this repo's sidecar locates `ADR-0024` at `decisions/ADR-0024-…md`, and a sidecar on `project-os-dev` locates `ADR-0011` at `decisions/ADR-0011-No-Permanent-Warning-Tier.md`. 14 tests, including that `[[README#Edit policy]]` and `[[ADR-9999]]` are untouched.

## Notes

**Why `#` and not `/`.** [[ADR-0024]] carries the reasoning, including the argument for `/` that was made on 2026-08-11 and withdrawn: it rested on the slash form resolving natively in a multi-repo Obsidian vault, which it does not — project-os links resolve by `aliases:`, not by path, and `project-os-dev/ADR-0011` is no more a real path than `project-os-dev#ADR-0011` is a real heading.
