---
type: "[[adr]]"
id: ADR-0008
aliases: ["ADR-0008"]
title: "The cockpit keeps retired status values readable; the vocabulary that validates is upstream's"
status: accepted
owner: user:edwin
created: 2026-07-26
updated: 2026-07-26
source: ["upstream:project-os-dev ADR-0012"]
decision: "Adopt upstream ADR-0012's hyphen-free vocabulary (`in-progress` → `doing`, `rolled-back` → `reverted`, `in-review` → `review`, `wont-fix` → `declined`) in every cockpit surface. Retired values are removed from the *canonical* bands but kept in a separate legacy map so a note still carrying one renders with its old colour instead of falling through to the default grey."
context: "The cockpit renders ten repos, not one. Upstream's vocabulary changes land in each of them only when someone runs the migration and syncs, so between an upstream ADR and a downstream migration there is a window — days or months — where a real corpus holds values the canonical vocabulary no longer knows. That window is the cockpit's problem, not upstream's."
alternatives:
  - "Keep retired values inside `BANDS`. Rejected: `BANDS` is what `validate-docs` and the parity suite read as the definition of legal, so a retired value living there would keep passing validation forever and the migration would never be forced."
  - "Drop retired values entirely and let unmigrated notes render grey. Rejected: the cockpit's job is to show a corpus as it is. A `wont-fix` issue in a repo nobody has migrated yet is not an unknown state — it is a known state under its old name, and colouring it grey tells the reader something false about it."
  - "Auto-rewrite on read (display `wont-fix` as `declined`). Rejected: the cockpit is a viewer; silently renaming what a note says would make the UI disagree with the file, which is exactly the class of drift ISS-0023 was filed about."
consequences:
  - "`statuses.py` gains `LEGACY_STATUS_BAND` — retired values mapped to the band they used to occupy. `band_of()` consults it after `STATUS_BAND`, so colour survives the migration window while membership does not."
  - "`VOCABULARY`, `COMPLETED_STATUSES` and the parity suite continue to read only the canonical bands, so a retired value never counts as legal, never satisfies Hide-completed, and never passes validation."
  - "A legacy value renders in its historical colour with no badge. Flagging it in the UI was considered and dropped: the validator already reports it, and a viewer nagging about someone else's unmigrated repo is noise in the wrong place."
  - "`LEGACY_STATUS_BAND` is expected to shrink to empty once the fleet is migrated. It is not a permanent tolerance layer — deleting an entry is the signal that a migration finished."
supersedes: ""
superseded: ""
related: [ADR-0006, ISS-0023, TST-0019]
---

# The cockpit keeps retired status values readable

## Context

Upstream [[project-os-dev#ADR-0012]] (project-os-dev) removes the four hyphenated status values. Adopting the new vocabulary here is not the interesting part — it is a find-and-replace across nine surfaces that TST-0019 verifies.

The interesting part is that **this repo's code renders ten corpora**, and they migrate on their own schedule. `sync-project-os.sh` pulls the template when someone runs it; `migrate-status-vocabulary.py` rewrites notes when someone runs it. Between an upstream decision and a downstream migration there is a window where a live corpus holds values the canonical vocabulary has retired. During that window the cockpit must render those notes, and it must not lie about them.

## Decision

Adopt the new vocabulary, and separate two concerns the codebase had been treating as one:

* **Membership** — which values are legal — stays exactly as narrow as upstream says. `BANDS`, `VOCABULARY` and `COMPLETED_STATUSES` carry only the canonical 41. A retired value is not legal, does not pass validation, and does not count as completed.
* **Rendering** — what colour a value gets — tolerates history. `LEGACY_STATUS_BAND` maps each retired value to the band it used to occupy, and `band_of()` falls back to it.

So an unmigrated `wont-fix` issue still renders in the archived colour it always had, while the validator still reports it as illegal and the migration still gets forced. The two answers were never the same question; the previous docstring in `statuses.py` conflated them by keeping legacy values inside `BANDS` "so a repo whose history predates a migration still renders" — which achieved rendering at the cost of making the values permanently legal.

## Consequences

See frontmatter. The one worth stating plainly: `LEGACY_STATUS_BAND` should shrink. Every entry in it is a migration somebody has not run yet, and removing the last entry is how this repo learns the fleet is consistent. If it is still full in a year, that is a finding about the fleet, not about this decision.
