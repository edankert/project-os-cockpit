---
type: "[[change]]"
id: CHG-20261021-The-Cockpit-Reads-Ride-Results-And-Owes-What-The-Release-Test-Owes
title: "The cockpit reads a ledger holding ride results, keeps every field it does not know, owes a check per platform as release-test.py does, and shows the hand-run budget on the release page"
status: merged
owner: user:edwin
created: 2026-10-21
updated: 2026-10-21
source: ["[[TASK-0678-The-Cockpit-Reads-Ride-Results-And-Counts-Owed-Checks-As-The-Release-Test-Does]]"]
commit: ""
pr: ""
impacts: ["src/project_os_cockpit/ledger.py", "src/project_os_cockpit/acceptance.py", "src/project_os_cockpit/publication.py", "src/project_os_cockpit/release_test_bundled.py", "src/project_os_cockpit/validate_docs_bundled.py", "desktop/src/renderer/renderer.ts", "desktop/src/renderer/validation-rows.ts", "tests/test_release_ride_compat.py"]
platforms: []
issues: ["[[ISS-0326-The-Cockpit-Refuses-A-Ledger-That-Holds-Ride-Results]]"]
features: []
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[project-os-dev#CHG-20261021-A-Command-Can-Cover-One-Platform-And-A-Release-Test-Can-Be-Ridden]]"]
---

# The cockpit reads ride results and owes what the release test owes

## Summary

A repo can now import a release ride into its ledger and keep using the cockpit. Before this change, one imported ride made the cockpit refuse the whole ledger, so the acceptance checks and the release test disappeared for that repo. The cockpit also now agrees with `release-test.py` about which checks a person owes on each platform, and the release page shows the sheet's hand-run budget under its owed count.

## What changed

- **Ride results are read.** A ledger entry with `method: "ride"` is accepted, as the template's validator accepts it. A ride entry with no `build` is refused, again as the validator refuses it.
- **A write keeps what it does not know.** When the cockpit records a result, it rewrites the ledger. It now writes back every entry field, evidence field and top-level key it read, including a ride entry's `build`. A copy of your-trainer's Android ledger reads back byte for byte.
- **Owed per platform.** A check is automated on a platform when it has `command:` or a `commands:` entry for that platform. On such a platform, `hand_steps:` keeps the check owed for those steps. The checks page, the release gate and the release test agree on this, because the cockpit reads both fields with the template's own `read_commands` and `read_hand_steps`. Asked about no platform, only `command:` counts, as upstream says.
- **The budget line.** A release that names a platform with a ledger shows the sheet's sentence under "Release gate · N unchecked", for example "Hand-run budget: 37 checks with 240 steps are owed by hand on Android. The limit is 10 checks. This release is 27 over it." It is also in the release payload as `gate.budget`. It blocks nothing.
- The template sync of project-os a76657d re-copied `release_test_bundled.py` and `validate_docs_bundled.py`. The Fleet health page has a label for the validator's new `CHECK-COMMANDS` code.

## What a person notices

- your-trainer's REL-0017 page reads "Release gate · 37 unchecked" with the budget line under it; `release-test.py --release REL-0017 --platform android` prints the same 37 and the same sentence.
- After a ride is imported, the checks it passed leave the checks page and the release test, and recording another result in the cockpit leaves the ride entries as they were.

## Verification

- `tests/test_release_ride_compat.py`: 15 tests, one group per change. Eleven deliberate mutations each make it fail: ride refused, a ride with no build accepted, unknown entry fields, `build`, top-level keys or evidence fields dropped on write, owed counted by `command:` alone, hand steps ignored, unusable hand steps ignored, another platform's command counted, and the budget not attached.
- Read-only against your-trainer REL-0017 on Android, the cockpit's owed set equals `release-test.py`'s on both platforms, and the budget line is the sheet's. Its ledger was copied for the write test and never written.
- The full Python suite passes (2253 passed, 11 skipped) and the desktop suite passes 229 tests.
