---
type: "[[task]]"
id: TASK-0603
aliases: ["TASK-0603"]
title: "The coverage gap is computed, not guessed — the features a release ships that no check names, and the requirements whose criteria nobody ticked"
status: done
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
owner: user:edwin
created: 2026-09-08
updated: "2026-09-08"
source: ["[[FEAT-0145-Preparing-A-Release-Is-One-Workflow]]", "Edwin, 2026-09-08: 'add new checks if required (these might be LLM/Human actions?)'"]
parent: "[[FEAT-0145-Preparing-A-Release-Is-One-Workflow]]"
effort: M
due: ""
depends: []
blocks: ["[[TASK-0604]]"]
related: ["[[REQ-0061-A-Release-Is-Written-Through-One-Workflow]]", "[[ADR-0032-The-Verification-Link-Has-One-Direction]]", "[[REQ-0059-A-Section-Is-Derived-Never-Filed]]"]
tests: []
---

# The coverage gap is computed, not guessed

*"Is anything this release ships not covered by a check?"* is exactly the sweep a person skips, and `your-trainer` is the evidence: three of PHASE-021's claims — the per-rider preferences, the power source in History, the Pro grant a data-only bike does not earn — had no check at all, and only a deliberate read of thirty task notes against nine checks found them.

**The tool's half is mechanical and stops there.** No model runs in this task, so the number on the page is reproducible and the same on every machine. Drafting the missing checks is [[TASK-0604]].

## Definition of Done

- [x] `publication.coverage_gaps(index, release_id="", content_ids=None)` returns two populations:
  - **uncovered** — a feature this release carries that no acceptance check names in `covers:`.
  - **unmet** — a requirement constraining one of those features with criteria nobody has ticked.
- [x] **The reverse index, not a second walk.** The predicate is the suite's own `refs` — the direction [[ADR-0032]] settled on and the one `_open_tests_for_contents` already reads. A fresh walk over `covers:` here is [[REQ-0059]]'s forbidden shape: a second implementation of a derivation that already exists.
- [x] **A feature carrying `acceptance_exception:` is not a gap.** Somebody wrote down why it needs no check; that is an answer, not an absence.
- [x] Unticked criteria come from `criteria.payload`, which is the module that already owns *"a criterion of record with no verification record"*.
- [x] The gaps render as their **own section** on the release page — not folded into the gate, which counts something else.
- [x] A release with no gaps says so in a sentence. An empty section that renders as nothing reads as a section that failed to load.
- [x] The scope follows the release's **contents**, so holding a feature back removes its gap along with its checks — the same subtraction [[ADR-0040]] performs on the gate.

## Steps

- [x] Write `coverage_gaps` in `publication.py`.
- [x] Wire it into `release_payload`.
- [x] Render the section.
- [x] Guard on a fixture with all four shapes: a covered feature, an uncovered one, one with `acceptance_exception:`, and a requirement with unticked criteria.

## Notes

**The number must be defensible.** This section is what an agent's prompt will name in [[TASK-0604]], so a gap list that is subtly wrong becomes a set of checks nobody needed. Prefer under-reporting — a feature whose coverage is ambiguous is not a gap — over a list a person learns to skim.
