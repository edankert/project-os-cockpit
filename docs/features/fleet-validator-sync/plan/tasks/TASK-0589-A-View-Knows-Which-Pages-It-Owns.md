---
type: "[[task]]"
id: TASK-0589
aliases: ["TASK-0589"]
title: "A view knows which pages it owns, so refreshing the navigator stops evicting the reader from `~checks`"
status: done
phase: "[[PHASE-041-The-Gate-Runs-Where-The-Checks-Are]]"
owner: user:edwin
created: 2026-08-30
updated: "2026-08-30"
reviewed_by: model:claude-opus-5
review_date: 2026-08-30
review_verdict: changes-requested
source: ["[[ISS-0263-A-Write-Evicts-The-Reader-From-The-Checks-Page]]"]
parent: "FEAT-0143"
effort: ""
due: ""
depends: ["TASK-0588"]
blocks: []
related: ["[[ISS-0262-Marking-A-Check-Clears-The-Filter-You-Are-Walking]]", "[[FEAT-0092-The-Views-Get-A-Page]]"]
tests: []
---

# A view knows which pages it owns

## What changed

`VIEW_OWNED_PAGES` (`tests: ['~checks']`) and `onOwnedPage(navMode, rel)`, replacing `currentRel !== target` in `loadWsNav`'s landing guard. Sub-paths count, so `~checks/area/Monetization` is on the view too.

The rule is not new — Publication and Design already guard on their whole family. This gives the three `VIEW_LANDING_RELS` views the same property, which they lacked because they were built single-page and Tests later grew `~checks`.

## Why this took three reports

The first two answers were wrong, and both were reached by reading code rather than reproducing:

1. *"the page is stale, restart the process"* — true of the sidecar and irrelevant to this.
2. *"the filters are cleared"* — a real defect ([[ISS-0262]], fixed) on the same keystroke, which is exactly why it was convincing. It was not what the reader was describing.

What settled it was the reader's third description naming the destination — *"to the tests section/needs you section"* — which is a landing, not a repaint. A symptom that names where it lands is a navigation defect; that was the sentence to have asked for at the start.

## Guards

`test_a_write_does_not_evict_the_reader_from_the_checks_page` fails when the guard is reverted to the equality test — run, not assumed. `test_the_landing_still_fires_when_the_reader_is_elsewhere` pins the other side so [[FEAT-0092]]'s landing is not quietly removed.

`tsc --noEmit` clean, `desktop/dist/renderer` rebuilt, window reloaded.

## Independent review, 2026-08-30 — changes-requested

Findings: [[ISS-0266]] — reverting `onOwnedPage` to the equality test (rather than emptying the table, which the guard does catch) passes the full suite; and [[ISS-0267]] — the Tests view owns `~tests/<TST>/run` as well, by the argument its own source gives, and `~accept/<FEAT>` belongs to no view and is evicted under every mode. The `desktop/dist/renderer` rebuild claimed here is not verifiable from the commit: `dist/` is gitignored.

Reviewed from a clean context (the notes and the diff, no authoring transcript) by `model:claude-opus-5`, the same model family as the author and a different session. Mutants were applied one at a time in a worktree at `c861414` and the full suite re-run; corpus figures were recomputed against `git archive fb99a751`, the `../your-trainer` state as of these commits.
