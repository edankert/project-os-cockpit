---
type: "[[change]]"
id: CHG-20260907-Links-In-The-Record-Resolve
aliases: ["CHG-20260907-Links-In-The-Record-Resolve"]
title: "Every link in the record resolves, three task notes that were zero bytes hold their work again, and a guard reads note bodies for the first time"
status: merged
owner: user:edwin
created: 2026-09-07
updated: 2026-09-07
source: ["Edwin, 2026-09-07: 'can you make sure they are all fixed because many are failing atm'"]
commit: ""
pr: ""
impacts: ["docs/features/overview-scopes/plan/tasks/TASK-0182-Nest-Children-By-Shared-Phase.md", "docs/features/agent-hooks/plan/tasks/TASK-0183-Revive-Ended-Session-On-Activity.md", "docs/features/embedded-terminal/plan/tasks/TASK-0187-Restart-Console-Action.md", "tests/test_record_links.py", "tests/test_surface_ownership.py", "tests/test_gate_delta.py", "tests/test_release_gate_campaign.py", "src/project_os_cockpit/cockpit.py"]
issues: ["[[ISS-0287-Broken-Links-In-The-Record]]"]
features: []
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[PHASE-015-Phase-Hygiene]]", "[[ISS-0162-The-Bare-Upstream-Citations-Still-Resolve-To-Nothing]]", "[[FEAT-0093-A-Note-In-Another-Project-Is-One-Click-Away]]"]
---

# Links in the record resolve

## Summary

Twenty-five links in note bodies pointed at nothing, and the cockpit drew each one as a broken link on the page. They are fixed. Three task notes that had been **zero-byte files since July** hold their work again. And a guard now reads links in note bodies, which nothing had ever done.

The external URLs were never the problem: all 28 resolve, and the weekly `link-check` workflow that checks them has been right every week. What it does not check — and what `validate-docs.py` does not check either — is the 7,076 wikilinks a reader actually clicks.

## Three notes were empty files

`TASK-0182`, `TASK-0183` and `TASK-0187` were committed at **0 bytes** on 21 and 22 July and stayed that way. The work shipped; the notes held nothing. Because they carry no frontmatter they were invisible to the snapshot, the navigator and every count — present enough to be linked to, absent from everything that reads the record.

They are reconstructed from their delivering commits (`15d732c`, `3536687`) and the issues they closed, each carrying a line saying so and on what date. Nothing is invented: where no test note existed, the note says that rather than claiming one.

## What the other links were

| cause | links |
| --- | --- |
| cited a zero-byte note | 4 |
| named a note under a different name | 8 |
| named a real file outside `docs/` | 10 |
| bracketed prose | 2 |
| a note in another repository | 1 |

The second group is the ordinary kind: `[[CHG-20260812]]` is a date without the title its filename carries, `[[PHASE-0002]]` is the four-digit id the project stopped using, `[[reference/HOSTED-COCKPIT]]` names a directory called `references/`.

The third is more interesting, because those links were not typos. `[[CLAUDE]]`, `[[INTENT]]`, `[[LIFECYCLE]]`, `[[STATUSES.md]]`, `[[TESTING]]` and `[[independent-review]]` all name real files — at the repository root, under `tools/instructions/`, under `tools/skills/`. The resolver walks `docs/` and nothing else, so a wikilink is the wrong form for them however they are spelled. Making them resolve would mean widening what the cockpit serves, which is a security boundary rather than a spelling question. They became inline code carrying the real path.

## The count was wrong twice before it was right

Worth recording, because the same mistake is easy to repeat.

A pass over raw text found **232** unresolved `[[…]]` occurrences. Wrong: 206 sit inside fenced blocks or inline code, where Markdown never makes a link. They are notes *about* the syntax — `[[FEAT-...]]`, `[[CHK-*]]` — written correctly.

Stripping code **line by line** then gave **26**. Also wrong, by one: an inline span may wrap across a line break, and a per-line pass pairs the stray backticks either side of the break into a span that was never opened, which reported a correctly backticked example in `docs/references/COCKPIT-API.md` as broken. Stripping over the whole document gives **25**.

The relative links went the same way: a first scan said 7 broken, and all seven are `![Alt](./image.png)` examples inside fenced blocks. **None were broken.**

## The guard

`tests/test_record_links.py`: every wikilink resolves, every relative link points at a file, no note is zero bytes. Each was mutation-checked by planting the defect it describes and watching it fail.

**It lives in `tests/` rather than in `tools/scripts/validate-docs.py`** because `tools/sync/MANIFEST.yaml` lists `tools/scripts/` as template-owned, so a check added there would report as divergence on the next upstream sync. The same reasoning that put the `review_response` rule in `CLAUDE.md`. It is proposed upstream; until then it is this repository's.

Without it this recurs. [[ISS-0162]] repaired 48 bare upstream citations by hand in August and closed; nine more had appeared by September. That is what a defect with no guard does.

## Restoring the notes turned three tests red, and each was resting on something it should not have been

**A guard that needs the corpus to stay broken.** `test_every_task_note_on_disk_is_reachable` asserted `typed < on_disk | typed` — a strict subset, meaning *at least one task note must be untyped*. That held only because these three were zero-byte files. Giving them frontmatter made every task typed and the guard failed on a repository that had just got healthier. The fallback it protects is still worth having, so the case is now constructed: an untyped note under `features/*/plan/tasks/` is swept in, and one that types itself as a test is not. `_task_records`' own docstring said *"three notes … have none"*, which is no longer true, and it now says so.

**A grammar check pinned to a number.** `test_the_historical_line_is_computed_from_the_real_tags` required the summary to read `12 releases, …` under a comment claiming *"the tag count is stable — tags do not move"*. Tags do not move; new ones get cut, and `your-trainer` cut a thirteenth. Now `\d+ releases`.

**An assertion about another repository's data.** `test_the_measured_repo_still_reports_what_this_phase_measured` checked that every blocking row in `your-trainer` names a subject. That property is already held on a fixture forty lines above it, by `test_a_blocking_row_names_its_subject`; the live copy was reading data quality, and it went red because one check there carries an empty `covers:`. Removed from the live test, which keeps only what is about this code.

**Two findings for `../your-trainer`, neither of them this repository's to fix:** `TST-0591` names no subject, and the gate reports **538 blocking** where it reported 3 the day before — an empty `WORKING-ios.json` appeared on 2026-09-06 at 17:55, and a platform with a ledger and no entries owes every check in the suite. That second one is already filed there as [[ISS-0286]].

## Verification

Zero unresolved wikilinks across 7,076 live ones, zero broken relative links, zero zero-byte notes. Each of the three new guards was mutation-checked. Validator green, full suite green.
