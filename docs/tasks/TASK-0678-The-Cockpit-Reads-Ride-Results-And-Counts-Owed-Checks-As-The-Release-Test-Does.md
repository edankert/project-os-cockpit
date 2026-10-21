---
type: "[[task]]"
id: TASK-0678
aliases: ["TASK-0678"]
title: "The cockpit reads a ledger holding ride results, keeps fields it does not know when it rewrites one, counts owed checks per platform as release-test.py does, and shows the hand-run budget"
status: done
phase: ""
owner: user:edwin
created: 2026-10-21
updated: 2026-10-21
source: ["[[ISS-0326-The-Cockpit-Refuses-A-Ledger-That-Holds-Ride-Results]]", "project-os a76657d"]
parent: "[[ISS-0326-The-Cockpit-Refuses-A-Ledger-That-Holds-Ride-Results]]"
effort: "M"
due: ""
depends: []
blocks: []
related: ["[[project-os-dev#TASK-0205]]", "[[project-os-dev#TASK-0206]]", "[[CHG-20261021-The-Cockpit-Reads-Ride-Results-And-Owes-What-The-Release-Test-Owes]]"]
tests: []
---

# The cockpit reads ride results and counts owed checks as the release test does

your-trainer's release ride (FEAT-0140) writes a results file on Edwin's tablet, and `release-test.py --import-ride` turns it into ledger entries with `method: "ride"` and a `build`. The cockpit has to read those entries, keep them intact when it writes the ledger, and agree with `release-test.py` about which checks are owed on each platform.

## Definition of Done

- [x] `ledger.check_entry` accepts `method: "ride"` and, as the template's validator does, refuses a ride entry with no `build`. A test reads a ledger holding a ride entry; it fails without the fix.
- [x] `Ledger.to_json` writes back every entry field, evidence field and top-level key it read and does not know, including `build`. A test appends a manual result to a copy of a ledger holding a ride entry, an unknown entry field, an unknown top-level key and an evidence item, and finds all of them in the file; it fails without the fix.
- [x] `acceptance.kind_of` treats a check as automated on the suite's platform when it has `command:` or `commands.<platform>`, and keeps it manual there when it also lists `hand_steps:`. A test shows a `commands: {android: ...}` check owed on iOS and not on Android, and a `hand_steps:` check owed on Android; it fails without the fix.
- [x] The bundled `release_test_bundled.py` and `validate_docs_bundled.py` are re-copied from the template sync of project-os a76657d, and the release page's owed count equals `release-test.py`'s owed set on a fixture with `commands:` and `hand_steps:`.
- [x] The release page carries the sheet's budget line under its owed count (`gate.budget` in the release payload, drawn by `buildGateSection`). A test reads it from the payload; it fails without the fix. *(Planned as the navigator's "Test them" row; moved to the release page because the navigator does not draw a row's subtitle, so a line there would be seen by nobody.)*
- [x] Read-only against your-trainer REL-0017 on Android, the cockpit's owed count and budget match `release-test.py`. The full Python suite passes.

## Result

All four are built, each with tests in `tests/test_release_ride_compat.py` (15 tests). Each test group was seen to fail without its fix: the ride group failed before `ledger.py` changed, and eleven mutations of the finished code each make the file fail (listed in [[CHG-20261021-The-Cockpit-Reads-Ride-Results-And-Owes-What-The-Release-Test-Owes]]).

- `ledger.py`: `METHODS` gains `ride`, and a ride entry with no `build` is refused. `Entry`, `Evidence` and `Ledger` keep the fields they do not read in `extra`, and `to_json` writes them back. `build` is written between `by` and `reason`, where the template's import puts it.
- `acceptance.py`: `Item` carries `commands`, `hand_steps`, `hand_steps_broken` and the `platform` it was loaded for. `kind_of` calls a check automated when `machine_only` holds: a command covers it on that platform and no usable hand step is left. Both fields are read with the bundled template's `read_commands` and `read_hand_steps`. A gate row's `command` is the command that runs the check on that platform, so a check that keeps a hand step gets its checkbox.
- `publication.py` and `renderer.ts`: the release payload's gate carries `budget` from the template's sheet for a release that names a platform with a ledger, and the release page prints its line under the owed count. `acceptance.release_test_budget` caches it on the same file signature as the release test page.
- The bundles were refreshed by syncing project-os a76657d with `sync-project-os.sh` and re-copying both files.

Measured read-only on your-trainer REL-0017, Android: the release gate reads 37 unchecked, and the budget is "Hand-run budget: 37 checks with 240 steps are owed by hand on Android. The limit is 10 checks. This release is 27 over it.", the same as `release-test.py`. The cockpit's owed set equals `release-test.py`'s on Android and iOS. A copy of its Android ledger reads back byte for byte; the file itself was not written. The full Python suite passes (2253 passed, 11 skipped) and the desktop suite passes 229.

Not done: `docs/__templates__/SCHEMAS.md` is merge-owned here and diverged from the template, so the sync left it, and the definitions of `commands`, `hand_steps`, `hand_run_limit` and the ride formats were not merged into it. The cockpit does not show a ride's `build` anywhere yet; project-os-dev ISS-0109 keeps "the cockpit showing imported results" open.
