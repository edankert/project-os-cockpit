---
type: "[[task]]"
id: TASK-0256
aliases: ["TASK-0256"]
title: "One History tile on the overview, replacing Activity, Changes and Commits"
status: done
phase: "[[PHASE-017-History-As-Document-Events]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["[[FEAT-0052-History-Timeline]]"]
parent: "[[FEAT-0052-History-Timeline]]"
effort: M
depends: ["[[TASK-0255-History-Payload]]"]
blocks: []
related: ["[[FEAT-0048-Changes-On-The-Overview]]", "[[PHASE-010-Surface-Ownership]]"]
tests: []
---

# The History tile

## Definition of Done
- [x] One `History` tile on the overview, and `buildActivityTile`, `buildChangesTile` and `buildCommitsTile` are **gone** — deleted, not hidden
- [x] Rows are transitions, each naming the item and where it went, and navigating to the note
- [x] Commits render as dividers carrying the short sha, date and subject — present but visually subordinate to the rows
- [x] Uncommitted work sits above the first divider, marked
- [x] A commit with no transitions still appears, flagged
- [x] Short: the recent window only, with a link to `~history`
- [x] The Activity sparkline survives in the tile header
- [x] Distinguishable without colour

## Steps
- [x] Build the tile from the new payload
- [x] Delete the three tiles and their fill functions; keep `commits_payload` and the `/api/cockpit/changes` endpoint, which the full view and other surfaces still use
- [x] Test: a source guard that the three builders are gone, plus a live pass

## Notes

**Deleting the three is the point.** Landing History beside them would leave the overview with four history surfaces — the shape [[PHASE-010]] and [[PHASE-012]] each closed by undoing. The guard should assert the *absence*, because that is the part that silently regresses.

**The sparkline is context, not a peer.** It answers "how busy", which is worth a strip above a list of events and is not worth a tile competing with them.

**CHG notes do not get their own tile any more, and do not disappear.** A change note is written *about* work, so it belongs in the row for the transition it explains — not in a parallel list. Where a transition has a CHG note, the row should say so.

## Done 2026-07-30

One `History` tile. `buildActivityTile`, `buildCommitsTile`, `buildChangesTile` and `fillCommits` are **deleted**, and a guard asserts their absence — that is the half that regresses silently.

Verified live: `document.querySelectorAll('.ov-tile h3')` returns exactly `["History"]`.

```
--- not committed yet · 3 files
    PHASE-017   History as document events…                      active
--- 07-30  04069e3  FEAT-0051: validator errors become session work…
    FEAT-0051   Validator errors are session work…               new · done
    TASK-0252   Subscribe the renderer to cockpit:validation…     new · done
--- 07-30  cebee80  ISS-0074: re-home sixteen delivered notes…
    ISS-0074    16 of the 19 notes naming PHASE-999 are terminal  new · fixed
```

`new · done` rather than `null → done` for a note born at its status; a real move renders `doing → done`.

**Kept, not deleted:** `commits_payload`, `/api/cockpit/changes` and `buildChangeRow` — the changes endpoint still serves other surfaces, and the commits payload still answers "what did this commit contain". Removing the *tile* is not removing the data.

**One polish from the live pass:** an untracked *directory* (git reports those as a single porcelain entry) and `SNAPSHOT.yaml` were rendering their path twice, once as the id and once as the title. The title is now empty when a row has no note behind it.
