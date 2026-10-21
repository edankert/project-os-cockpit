---
type: "[[task]]"
id: TASK-0678
aliases: ["TASK-0678"]
title: "The cockpit reads a ledger holding ride results, keeps fields it does not know when it rewrites one, counts owed checks per platform as release-test.py does, and shows the hand-run budget"
status: doing
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
related: ["[[project-os-dev#TASK-0205]]", "[[project-os-dev#TASK-0206]]"]
tests: []
---

# The cockpit reads ride results and counts owed checks as the release test does

your-trainer's release ride (FEAT-0140) writes a results file on Edwin's tablet, and `release-test.py --import-ride` turns it into ledger entries with `method: "ride"` and a `build`. The cockpit has to read those entries, keep them intact when it writes the ledger, and agree with `release-test.py` about which checks are owed on each platform.

## Definition of Done

- [ ] `ledger.check_entry` accepts `method: "ride"` and, as the template's validator does, refuses a ride entry with no `build`. A test reads a ledger holding a ride entry; it fails without the fix.
- [ ] `Ledger.to_json` writes back every entry field, evidence field and top-level key it read and does not know, including `build`. A test appends a manual result to a copy of a ledger holding a ride entry, an unknown entry field, an unknown top-level key and an evidence item, and finds all of them in the file; it fails without the fix.
- [ ] `acceptance.kind_of` treats a check as automated on the suite's platform when it has `command:` or `commands.<platform>`, and keeps it manual there when it also lists `hand_steps:`. A test shows a `commands: {android: ...}` check owed on iOS and not on Android, and a `hand_steps:` check owed on Android; it fails without the fix.
- [ ] The bundled `release_test_bundled.py` and `validate_docs_bundled.py` are re-copied from the template sync of project-os a76657d, and the release page's owed count equals `release-test.py`'s owed set on a fixture with `commands:` and `hand_steps:`.
- [ ] The release page's "Test them" row carries the sheet's budget line. A test reads it from the row; it fails without the fix.
- [ ] Read-only against your-trainer REL-0017 on Android, the cockpit's owed count and budget match `release-test.py`. The full Python suite passes.
