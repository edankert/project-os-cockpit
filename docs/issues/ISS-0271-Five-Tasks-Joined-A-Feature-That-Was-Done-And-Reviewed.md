---
type: "[[issue]]"
id: ISS-0271
aliases: ["ISS-0271"]
title: "Five UI and server tasks joined a `done`, already-reviewed feature about migrating validators — FEAT-0143's goal and its `acceptance_exception` now describe neither its task list nor the behaviour that shipped, and no CHG note was written"
status: triage
owner: user:edwin
created: 2026-08-30
updated: "2026-08-30"
severity: medium
component: docs
phase:
source: ["Independent review of 46d6593..c861414, 2026-08-30, model:claude-opus-5, fresh context"]
related: ["[[FEAT-0143-The-Fleet-Runs-One-Validator]]", "[[TASK-0587-The-Derived-Set-Is-This-Releases-Platforms]]", "[[TASK-0588-A-Write-Is-Not-A-Navigation]]", "[[TASK-0589-A-View-Knows-Which-Pages-It-Owns]]", "[[TASK-0590-A-Write-Is-Readable-When-It-Answers]]", "[[TASK-0591-Retiring-Removes-The-Obligation]]"]
tests: []
---

# The parent no longer describes the children

## What the diff does

`46d6593..c861414` appends `TASK-0587`..`TASK-0591` to `FEAT-0143`, and `FEAT-0143` is:

- `status: done`;
- carrying `reviewed_by: model:claude-opus-5`, `review_date: 2026-08-29`, `review_verdict: changes-requested`, and a `review_response` that enumerates the work reviewed;
- described by the goal *"Move every fleet repo onto the upstream validator … and leave a drift check behind that fails the build when the fleet falls behind again"*;
- waived from acceptance by `acceptance_exception: "This feature ships no user-facing surface: it is a migration of four repos' pre-commit tooling plus a CI check. Its observable behaviour is validate-docs.py exiting 0 …"`.

The five tasks are a release page's platform scoping, two renderer behaviours on `~checks`, a server re-index before a response, and the acceptance suite dropping retired checks. None of them migrates a repo onto a validator, and three of them are **exactly** a user-facing surface: the reader's filters, the page they are standing on, and which rows the suite shows.

## Why this is not bookkeeping

1. **The waiver is now false.** `acceptance_exception` is the field that excuses a feature from carrying acceptance checks, and its justification is a factual claim about the feature's scope. Five tasks later that claim does not hold, and the waiver is still standing on it.
2. **The review no longer covers the feature.** [[independent-review]]'s whole basis is that a verdict is about a specific artifact. Appending work to a reviewed, closed feature moves what the recorded verdict points at without changing the verdict — the field says `2026-08-29` and the newest task under it is dated the 30th.
3. **The traceability is wrong in the other direction too.** A later reader asking *"why was the checks page repaint split from the render?"* is routed to a feature about fleet validator migration.

## And no CHG note

`QUALITY.md`: *"If behavior/paths/contracts changed, create a `CHG-*` note and link it."* Five behaviours changed — what a release page offers, what the navigator lists, what a mark does to the reader's filters and position, when a write becomes readable, and whether a retired check gates a release across every repo the gate reaches. `docs/changes/` gained nothing. The precedent in this repo is the other way: `CHG-20260825-The-Console-Stops-Clipping-Its-Last-Line.md` is a single UI fix with its own change note.

That omission also silently skipped a trigger: the independent-review skill fires on *"a change carries a `CHG-*` note"*, so not writing one is how a change of this size can reach `main` unreviewed.

## Next Actions

- [ ] Give these five tasks a parent that describes them, or restate FEAT-0143's goal and re-open it.
- [ ] Re-check `acceptance_exception` against whatever the parent ends up being.
- [ ] Write the CHG note for the five behaviour changes.
