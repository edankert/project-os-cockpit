---
type: "[[adr]]"
id: ADR-0006
aliases: ["ADR-0006"]
title: "Retire the delivered band — upstream ADR-0008 deleted its last two members"
status: accepted
owner: user:edwin
created: 2026-07-25
updated: 2026-07-25
source: ["upstream:project-os-dev ADR-0008"]
decision: "Remove the `delivered` palette band, its CSS token, and its two members from every status surface. `DELIVERED_STATUSES` becomes an empty frozenset rather than disappearing, so callers need not branch on its absence; the parity test now asserts the retirement instead of the band's contents"
context: "ISS-0023 introduced `delivered` for work shipped but not signed off, with `implemented` as its founding member. ADR-0007 made `implemented` terminal and moved it to `done`, leaving `staged` and `monitoring`. Upstream ADR-0008 then deleted both after measuring zero writes of either across 5,890 status writes in 10 repos — leaving a coloured band that no status could enter"
alternatives:
  - "Keep `staged`/`monitoring` as an ADR-0008 exception, as `failing` was kept — rejected: `failing` is retained because ADR-0010 makes it reachable by stamping test status from execution. Nothing makes `staged` or `monitoring` reachable; they would be permanently empty rather than temporarily unused"
  - "Keep the band and repopulate it from the collapsed vocabulary — rejected: no surviving status means 'shipped but not signed off'. Inventing a member to justify a band inverts the reasoning"
  - "Leave the band defined but empty — rejected: `test_delivered_ranks_between_pending_and_done` computes min/max over its members and raises on an empty band, and dead palette entries are exactly the drift ISS-0023 was filed about"
consequences:
  - "`BANDS`, `BAND_TOKEN`, `STATUS_RANK`, both stylesheets and the desktop renderer lose the band; `--status-delivered` is deleted from both themes"
  - "`DELIVERED_STATUSES` is kept as an empty frozenset for call-site compatibility and should be deleted once no surface references it"
  - "`test_delivered_is_not_completed` is replaced by `test_delivered_band_is_retired`, which fails if the band is reintroduced without a decision; `test_delivered_ranks_between_pending_and_done` becomes `test_pending_ranks_below_done`"
  - "`ready` moves from the active band to pending — a test at `ready` is defined but not yet executed (ADR-0008/ADR-0010), which is 'not started', not 'in flight'"
  - "The Hide-completed set is unchanged: it was always done|archived, and delivered was only ever an exclusion from it"
supersedes: ""
superseded: ""
related: [ISS-0023, ISS-0025]
---

# Retire the delivered band

## Context

The band's whole history is three decisions long, and it never held a status anyone wrote.

`ISS-0023` created it because six status tables disagreed about `implemented`: coloured and ranked with the done family, yet never hidden by Hide-completed and unranked in the tasks pane. The fix introduced a `delivered` band meaning *shipped, not yet signed off*, with `implemented` as its founding member.

`ADR-0007` (upstream) then retired the requirement `verified` status and made `implemented` terminal, so it moved to `done`. The band was left with `staged` — a release verified and ready but not live — and `monitoring` — a risk mitigated but still watched. Both genuinely non-terminal, so the band was still defensible.

`ADR-0008` (upstream, 2026-07-25) deleted both, having reconstructed all 5,890 `status:` writes across the fleet from git history: **`staged` was written zero times, `monitoring` zero times.** The distinction the band drew was real; nobody ever expressed it.

## Decision

Retire the band. A palette band no status can enter is not a distinction the system makes, and keeping one is the same class of drift ISS-0023 was filed to remove — a surface asserting a vocabulary the corpus does not use.

The guard is kept rather than deleted: `test_delivered_band_is_retired` asserts the band, its token, and its two members are absent, so reintroducing it requires re-deciding it.

## Consequences

See frontmatter. Worth stating plainly: this partly unwinds ISS-0023's UI change of 2026-07-22, three days after it shipped. That is not a reversal of ISS-0023's finding — the six-way disagreement about `implemented` was real and its canonical-vocabulary fix (`statuses.py`) is what made this change a nine-line edit plus a test rewrite instead of an eight-surface hunt. What is unwound is only the band, and only because the measurement that justified it was never taken until ADR-0008 took it.
