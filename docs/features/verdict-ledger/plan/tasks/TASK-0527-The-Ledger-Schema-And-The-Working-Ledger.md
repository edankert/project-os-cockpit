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

- [ ] File schema documented: `release`, `version`, `platform`, `sealed`, `entries[]`.
- [ ] Entry schema documented: `check`, `mark`, `date`, `by`, `method`, `reason`; or `check`, `invalidated_by`, `date`.
- [ ] Exactly one open ledger per platform, created on demand.
- [ ] Sealing is a single operation: stamp `release`/`version`/`sealed`, rename, start a fresh working ledger.
- [ ] **Sealing expires `excused`** and carries `pass`/`partial`/`na` forward ([[ADR-0037]] decision 7). This is the one behaviour of the seal that is not bookkeeping.
- [ ] `docs/releases/ledgers/README.md` explains the working-to-sealed lifecycle for a human opening the directory.

## Notes

**JSON, not a note** — Edwin, 2026-08-19, and the measurement supports it over this note's first draft: `yaml.dump`/`yaml.safe_dump` occur **zero times** in `src/` and `tools/scripts/`, so PyYAML is a read-only dependency and a YAML ledger would introduce the project's first hand-rolled YAML writer, on the file a CI runner appends to on every green build. `json.dumps` is stdlib and total, and YAML's implicit typing (`no` → `False`, bare dates → `date`) is a hazard on a file of ids, dates and short words.

[[ADR-0030]] rejected [[FEAT-0112]]'s JSON, and **that objection does not reach this file**: FEAT-0112's was a *projection* of state the notes already held, which is what made the tool mandatory to edit a check. This holds state that exists nowhere else. The line [[ADR-0009]] draws is derived-versus-authored, not JSON-versus-frontmatter.

**It lives with its subject** ([[ADR-0020]]). A ledger is about a release.

**Sealing is what assigns an event to a release**, which answers [[ISS-0206]]'s third question without adding a field to anything.
