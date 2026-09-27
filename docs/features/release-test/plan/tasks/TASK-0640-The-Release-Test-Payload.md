---
type: "[[task]]"
id: TASK-0640
title: "The release test payload: per platform, its sections with progress, and per section what changed, Setup in three parts, and grouped checks"
status: backlog
phase: "[[PHASE-043-The-Walk-Page]]"
owner: user:edwin
created: 2026-09-27
updated: 2026-09-27
source: ["Edwin, 2026-09-27: approved example page"]
parent: "[[FEAT-0155-The-Release-Test-Goes-Section-By-Section]]"
effort: "L"
due: ""
depends: ["[[TASK-0639-Rename-The-Walk-To-The-Release-Test]]"]
blocks: ["[[TASK-0641-The-Release-Test-In-The-Tests-Pane]]", "[[TASK-0642-The-Platform-Overview-Continue-And-Needs-You]]", "[[TASK-0643-The-Section-Page-And-Its-Results]]"]
related: ["[[REQ-0067-The-Walk-Keeps-Required-Actions-And-Only-Relevant-Setup]]", "[[REQ-0070-The-Release-Test-Is-An-Overview-And-One-Page-Per-Section]]"]
tests: []
---

# The release test payload

## Definition of Done

- [ ] The API returns, for one release and one platform: the version, the sections in order, and per section its title, check count and one "on the bench" line.
- [ ] Per section it also returns: what changed for this platform only, grouped by screen, one line per change, with before and after capture paths and a stale flag when a capture is older than the latest change to its screen; Setup as three lists ("On the bench", "Before you start", "Later"); and the checks in groups.
- [ ] Each group has a heading and an optional "Start:" line. Each check has a number within the section, one action line, one expected line, its test tag, and, when it cannot be done yet, a reason and a suggested result.
- [ ] The expected line is the check's own words from its test note's `## Expect` (decision D2), not a copy held elsewhere.
- [ ] The set of test notes in the payload equals `ledger.owed` for the platform, asserted by a test on Your Trainer's corpus, as `tests/test_walk_payload.py` does today.
- [ ] Nothing in the payload is a duration or an estimate.

## Steps

- [ ] Read what project-os-dev's release test generator returns once it exists; do not work out sections, groups, "Start:" lines or what changed in the cockpit.
- [ ] Map it onto the payload above and add fixture tests for both platforms.

## Notes

This task only carries data the generator produces. Where the generator does not yet give a field the page needs, file it upstream rather than computing it here. Row results stay in the browser, keyed by workspace, release, platform, section and check, as Edwin decided for step results on 2026-09-14 (FEAT-0150); the ledger receives one event per test note.
