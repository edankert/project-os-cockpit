---
type: "[[task]]"
id: TASK-0640
title: "The release test payload: per platform, its sections with progress, and per section what changed, Setup in three parts, and grouped checks"
status: done
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

- [x] The API returns, for one release and one platform: the version, the sections in order, and per section its title, check count and one "on the bench" line. `release_test_payload` returns the generator's `payload()`: `version`, sections in order, each with its name, `count` of printed checks and `bench_line`.
- [x] Per section it also returns: what changed for this platform only, grouped by screen, one line per change, with before and after capture paths and a stale flag when a capture is older than the latest change to its screen; Setup as three lists ("On the bench", "Before you start", "Later"); and the checks in groups. `what_changed` screens for this platform with before/after capture paths and `stale`; `setup.bench`, `setup.before`, `setup.later`; `groups`.
- [x] Each group has a heading and an optional "Start:" line. Each check has a number within the section, one action line, one expected line, its test tag, and, when it cannot be done yet, a reason and a suggested result. `title`, `start`; each check `number`, `action`, `expected` (text and tags), `tags`, `readiness` with its suggested `result`.
- [x] The expected line is the check's own words from its test note's `## Expect` (decision D2), not a copy held elsewhere. The generator expands a tag-only line to the check's own Expect text (ADR-0049); nothing in the cockpit holds a copy.
- [x] The set of test notes in the payload equals `ledger.owed` for the platform, asserted by a test on Your Trainer's corpus, as `tests/test_walk_payload.py` does today. `test_on_your_trainer_the_page_is_what_is_owed_plus_what_this_release_recorded`, both platforms: the page is `ledger.owed` plus exactly the notes the open ledger has a clearing result for, because the page shows what the release owed.
- [x] Nothing in the payload is a duration or an estimate. The generator writes none (TESTING.md rule 8); `timer` is an authored wait, as before.

## Steps

- [ ] Read what project-os-dev's release test generator returns once it exists; do not work out sections, groups, "Start:" lines or what changed in the cockpit.
- [ ] Map it onto the payload above and add fixture tests for both platforms.

## Notes

This task only carries data the generator produces. Where the generator does not yet give a field the page needs, file it upstream rather than computing it here. Row results stay in the browser, keyed by workspace, release, platform, section and check, as Edwin decided for step results on 2026-09-14 (FEAT-0150); the ledger receives one event per test note.

## Close-out, 2026-09-27

**What the release owed, not what it still owes.** A check whose result lands in the open ledger stops being owed, and a page rebuilt after each result would lose it. The payload sets the open ledger's results aside while building the page, and returns them in `results`. An invalidation after a result drops it. Tested in `tests/test_release_test_route.py`.

A platform with no open release note of its own is tested against the newest open one: your-trainer's REL-0017 names Android only, and v2.2.0 is tested on iOS too.
