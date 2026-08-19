---
type: "[[task]]"
id: TASK-0527
aliases: ["TASK-0527"]
title: "Define the ledger file — schema, the working ledger per platform, and sealing at release cut"
status: backlog
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
parent: "[[FEAT-0133-The-Ledger-Is-The-Only-Place-A-Verdict-Lives]]"
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
tags: [task]
---

# The ledger file

`docs/releases/ledgers/REL-####-<platform>.json`, open one at `WORKING-<platform>.json`.

## Definition of Done

- [x] File schema: `release`, `version`, `platform`, `sealed`, `entries[]`, `evidence[]`.
- [x] Entry schema: `check`, `mark`, `date`, `by`, `method`, `reason`; or `check`, `invalidated_by`, `date`.
- [x] **`evidence` is a sibling collection of `entries`**, joining by `check` + `date`.
- [x] Exactly one open ledger per platform, created on demand.
- [x] Sealing stamps `release`/`version`/`sealed`, renames, and starts a fresh working ledger.
- [x] **Sealing expires `excused`** and carries `pass`/`partial`/`na` forward.
- [ ] `docs/releases/ledgers/README.md` explains the lifecycle for a human opening the directory.

## Done 2026-08-19 — `src/project_os_cockpit/ledger.py`, 24 tests

**The resolution rule is three lines and each is a decision.** A later terminal entry supersedes an earlier one; an invalidation clears the standing verdict; and **an entry that does not persist is dropped when its ledger seals**. `PERSISTS` is `{pass, partial, na}` — everything else was a statement about *that* release, including `fail`, `blocked` and `question`, which would otherwise still read `fail` in December against a build nobody ships.

**A bug the format found by being exercised rather than read.** `_platform_of` split the filename on its *first* hyphen, so `REL-0012-android` parsed as platform `0012-android` — matching no filter. **A ledger disappeared from its own platform the moment it was sealed**, and every verdict in it silently stopped counting: silent, and in the direction that lets a release through. It is anchored on the prefix now (`WORKING` or `<TYPE>-####`) and pinned by `test_a_sealed_ledger_stays_on_its_own_platform`.

**Mutation-proven on the two properties a cleanup would flatten first**: adding `excused` to `PERSISTS` fails the expiry test; restoring the first-hyphen split fails two.

## Notes

**JSON, not a note** — Edwin, 2026-08-19, and the measurement supports it over this note's first draft: `yaml.dump`/`yaml.safe_dump` occur **zero times** in `src/` and `tools/scripts/`, so PyYAML is a read-only dependency and a YAML ledger would introduce the project's first hand-rolled YAML writer, on the file a CI runner appends to on every green build. `json.dumps` is stdlib and total, and YAML's implicit typing (`no` → `False`, bare dates → `date`) is a hazard on a file of ids, dates and short words.

[[ADR-0030]] rejected [[FEAT-0112]]'s JSON, and **that objection does not reach this file**: FEAT-0112's was a *projection* of state the notes already held, which is what made the tool mandatory to edit a check. This holds state that exists nowhere else. The line [[ADR-0009]] draws is derived-versus-authored, not JSON-versus-frontmatter.

**It lives with its subject** ([[ADR-0020]]). A ledger is about a release.

**Sealing is what assigns an event to a release**, which answers [[ISS-0206]]'s third question without adding a field to anything.
