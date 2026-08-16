---
type: "[[task]]"
id: TASK-0442
aliases: ["TASK-0442"]
title: "Delete the walker, both Prepare controls, the release-gate group and the Needs-you duplication"
status: done
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["[[FEAT-0107]]", "Independent review of PHASE-034, 2026-08-16"]
parent: "[[FEAT-0107-Publication-Is-A-List-Of-Releases]]"
effort: S
depends: []
blocks: []
related: ["[[ADR-0028-Work-Has-Three-Phases]]"]
tests: []
---

# Delete the walker, both Prepare controls, the release-gate group and the Needs-you duplication

## Why

Nothing is added. This is the commit where the surface gets smaller and Edwin can see it before anything new lands.

## Definition of done

- [x] `~walk`, `renderAcceptanceWalkPage`, `buildAcceptanceWalker`, `GateCheck` and the walk-check pass/fail path are gone, with `TST-0029`/`TST-0030` superseded rather than deleted — deleted; TST-0029/0030 kept as the record, and the vocabulary gap that made retiring them impossible is filed as ISS-0178
- [x] `prepare_release` (`cockpit.py:4171`), its render branch (`renderer.ts:10215`), `promptPrepareRelease` and `~prepare-release` are gone — all four gone — the version field on the release page is the only way to start a release
- [x] The `release-gate` navigator group is gone — gone; the suite is reachable from the release page and from Tests, where it already lived
- [x] `publication` joins `_VIEWS_THAT_ALREADY_GATHER` — done — the same commits stopped appearing in `Needs you` and `To push` adjacently
- [x] The `To commit` placeholder row and the unread group-level `needs_human`/`owed_verb` are gone — group-level `needs_human`/`owed_verb` removed; no renderer read them
- [x] The dead `Item.anchor` duplicate and the doubled `excepted` key in `acceptance.py` are gone — both gone
- [x] `tests/test_acceptance_walker.py:299` — which currently asserts the defect — is removed with it — the whole file is gone — its release-creation coverage was already duplicated in `test_release_lifecycle.py`
- [x] Full suite green, and the diff is net NEGATIVE — **1377 passed**, and the diff removes ~19k characters of source against ~2k added


## Done 2026-08-16

Pure deletion, as agreed. Publication's navigator went from **seven groups to five**, and three of the nine concepts the review counted are gone.

Two things the cut surfaced that the plan did not anticipate:

- **A test cannot be retired.** `STATUSES.md` gives a test `ready`/`passing`/`failing` and no terminal status, while every other type has one — so a test whose subject was deleted must either keep claiming to verify it or be deleted, and LIFECYCLE.md forbids the second. Worked around with `ready` plus a section saying what happened; filed as [[ISS-0178]] for an upstream proposal.
- **The coverage guard caught the retirement note itself**, because it named a test function the cut had deleted. It was right to: a note must not name a test that does not exist, even when the note is about its removal. Reworded rather than exempted.

`acceptance.locate`, `rewrite_check` and `check_map` are kept although nothing calls them now — they are the addressing the exception path needs and are covered by `test_acceptance_exceptions.py`. That is a deliberate exception to the ISS-0139 rule and is recorded here so it is a decision rather than an oversight.
