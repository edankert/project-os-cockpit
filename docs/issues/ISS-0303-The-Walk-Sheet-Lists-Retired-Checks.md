---
type: "[[issue]]"
id: ISS-0303
aliases: ["ISS-0303"]
title: "The generated walk sheet lists retired checks; the walk page does not, so the two disagree about what a release owes"
status: fixed
severity: medium
phase: "[[PHASE-999-Future]]"
owner: user:edwin
created: 2026-09-13
updated: 2026-09-13
source: ["Comparing tools/scripts/walk-sheet.py against acceptance.walk_payload on this repo, 2026-09-13"]
area: "the walk"
component: "tools/scripts/walk-sheet.py"
severity_note: ""
affects: ["[[FEAT-0149-The-Walk-Page]]"]
related: ["[[TASK-0618-The-Walk-Payload]]", "[[ISS-0249-Retire-A-Check-From-The-View]]"]
tags: [issue, acceptance, upstream]
---

# The walk sheet lists retired checks

## What happens

`tools/scripts/walk-sheet.py --release REL-0002 --platform macos` reports **5 owed rows** on this repo. `~walk/macos` reports **4**. The extra row is `TST-0085`, which carries `status: retired`.

## Why it matters

Retiring a check means *kept, and no longer asked* ([[ISS-0249-Retire-A-Check-From-The-View]]). The verdict and its date survive as the record that a behaviour was once walked; what stops is the asking. A sheet that prints a retired check asks it, so the one thing retirement does is undone by the document a walker actually reads.

And the two surfaces disagree about one corpus, which is the specific failure the bundling decision was taken to prevent. Here the disagreement is not in the bundled rules — it is in what gets loaded before they run. `acceptance.load` drops retired items in one place (`_is_retired`, added so the gate, the tiers and the facets cannot disagree); `walk_sheet.load_checks` filters on `type` and `level` and never reads `status`.

## Where it is

Upstream, in `tools/scripts/walk-sheet.py`, `load_checks`. The cockpit's page is already correct, because it passes its own suite in rather than letting the module load one — so nothing here needs fixing and nothing here can fix it.

```
grep -n "def load_checks" -A 12 tools/scripts/walk-sheet.py   # no status test
grep -n "_is_retired" src/project_os_cockpit/acceptance.py    # the cockpit's
```

## What a fix looks like

`load_checks` skips a note whose `status:` is `retired` (and `superseded`, for the same reason). It belongs beside the `level: acceptance` test, and it is one line. **Not a fix to make here**: the bundled copy is asserted byte-identical to upstream's (`tests/test_walk_bundle.py`), and patching it locally is how the two versions of a shared rule start to drift.

## Owner

project-os-dev, FEAT-0029. File it there; this note records the finding and the measurement that produced it.

## Why this is parked under PHASE-999 and not under PHASE-043

It was found by PHASE-043 and it is not PHASE-043's to fix: the file is upstream's and the bundled copy here is asserted byte-identical to it. A phase cannot close while a note naming it in `phase:` is unresolved, and holding this phase open for a repair that belongs in another repository would make its status say something false. The relationship is kept in `related:`, which is what records where it came from.

## Fixed upstream, 2026-09-13

`tools/scripts/walk-sheet.py` `load_checks` now skips a note whose `status:` is `retired`, beside the `level: acceptance` test, exactly as this note said it should. `tools/scripts/test-walk-sheet.sh` asserts it, and removing the filter fails two assertions.

**The fix is narrower than this note proposed, and the difference is the point.** Adding `superseded` beside `retired` "for the same reason" introduced a *second* disagreement: `acceptance._is_retired` matches `retired` alone, `superseded` is not a legal status for a `[[test]]` (`STATUSES.md` `[[test]]`), and the sheet then reported one fewer owed row than the page. One disagreement fixed by introducing another is not a fix. The filter reproduces `_is_retired` and nothing more, and the harness asserts that a check at an unfiltered status is still asked.

**Measured after the fix.** On this repo the two agree at 3 owed on macos, loading the same 38 manual checks. On your-trainer the correction is much larger — 217 retired checks, and its REL-0017 android sheet goes from 61 owed rows to 39 — so the cost of this defect was mostly borne there.

`src/project_os_cockpit/walk_sheet_bundled.py` has been re-copied and `tests/test_walk_bundle.py` passes.
